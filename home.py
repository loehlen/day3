# home.py
# This is the entry point of our Streamlit app — the file Streamlit runs
# when the app starts.

import streamlit as st
from dotenv import load_dotenv
import os
import re
import json
from pypdf import PdfReader
from openai import OpenAI
import numpy as np

from elements import CONTRACT_ELEMENTS, ELEMENTS_BY_ID, FORMATION_ELEMENT_IDS
from rules import RULE_FUNCTIONS
from docx_export import build_docx

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(page_title="Contract Formation Checker")
st.title("Contract Formation Checker")
st.write("Upload a contract, or paste in a scenario, and I'll check it against the elements of contract formation.")

if "raw_text" not in st.session_state:
    st.session_state["raw_text"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


# --- Helper functions ---

def extract_text_from_pdf(file) -> str:
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text


def split_into_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s]


def chunk_text(text: str, sentences_per_chunk: int = 4, overlap: int = 1) -> list[str]:
    sentences = split_into_sentences(text)
    chunks = []
    step = sentences_per_chunk - overlap
    for i in range(0, len(sentences), step):
        chunk = sentences[i:i + sentences_per_chunk]
        if chunk:
            chunks.append(" ".join(chunk))
        if i + sentences_per_chunk >= len(sentences):
            break
    return chunks


def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text,
    )
    return response.data[0].embedding


def cosine_similarity(a: list[float], b: list[float]) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def find_relevant_chunks(query: str, chunks: list[str], chunk_embeddings: list[list[float]], top_n: int = 2) -> list[str]:
    query_embedding = get_embedding(query)
    scored_chunks = [
        (chunk, cosine_similarity(query_embedding, chunk_embedding))
        for chunk, chunk_embedding in zip(chunks, chunk_embeddings)
    ]
    scored_chunks.sort(key=lambda pair: pair[1], reverse=True)
    return [chunk for chunk, score in scored_chunks[:top_n]]


def extract_facts(relevant_text: str, element: dict) -> dict:
    facts_list = "\n".join(f"- {fact}" for fact in element["facts_needed"])
    prompt = f"""You are extracting facts from a contract for legal analysis. \
Do not give legal conclusions or opinions — only report what the text \
states or clearly implies.

Contract text:
\"\"\"
{relevant_text}
\"\"\"

For the element "{element['name']}", extract these facts:
{facts_list}

Return ONLY a JSON object with each fact name as a key. Use the value \
true, false, or "unclear" for each — "unclear" if the text does not \
say enough to determine it. No extra commentary, no markdown fences."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)


def ask_follow_up(scenario_text: str, element_results: dict, question: str) -> str:
    """
    Answers a follow-up question, giving the model the original text and
    the analysis already performed, so it can answer in context.
    """
    results_summary = "\n".join(
        f"- {ELEMENTS_BY_ID[eid]['name']}: {'Met' if r['met'] else 'Not met'} — {r['reason']}"
        for eid, r in element_results.items()
    )
    prompt = f"""Contract/scenario text:
\"\"\"
{scenario_text[:3000]}
\"\"\"

Analysis so far:
{results_summary}

Follow-up question: {question}

Answer the follow-up question, referring to the analysis and the contract text where relevant."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content


# --- Input ---
uploaded_file = st.file_uploader("Upload a contract (PDF or .txt)", type=["pdf", "txt"])
st.write("— or —")
pasted_text = st.text_area("Paste in a contract or scenario", height=200)

if uploaded_file is not None:
    st.session_state["input_source"] = "file"
    if uploaded_file.name.endswith(".pdf"):
        st.session_state["raw_text"] = extract_text_from_pdf(uploaded_file)
    else:
        st.session_state["raw_text"] = uploaded_file.read().decode("utf-8")
elif pasted_text:
    st.session_state["input_source"] = "text"
    st.session_state["raw_text"] = pasted_text


# --- Analysis pipeline ---
if st.session_state.get("raw_text"):
    scenario_text = st.session_state["raw_text"]
    chunks = chunk_text(scenario_text)

    if "chunk_embeddings" not in st.session_state or st.session_state.get("embedded_chunks") != chunks:
        with st.spinner("Generating embeddings for each chunk..."):
            st.session_state["chunk_embeddings"] = [get_embedding(c) for c in chunks]
            st.session_state["embedded_chunks"] = chunks

    element_results = {}
    with st.spinner("Analysing against each element of contract formation..."):
        for element in CONTRACT_ELEMENTS:
            relevant = find_relevant_chunks(element["query"], chunks, st.session_state["chunk_embeddings"])
            relevant_text = " ".join(relevant)
            facts = extract_facts(relevant_text, element)
            verdict = RULE_FUNCTIONS[element["id"]](facts)
            element_results[element["id"]] = verdict

    st.session_state["element_results"] = element_results

    # --- Results display ---
    contract_formed = all(element_results[eid]["met"] for eid in FORMATION_ELEMENT_IDS)
    st.session_state["contract_formed"] = contract_formed

    st.subheader("✅ Contract likely formed" if contract_formed else "❌ Contract likely NOT formed")

    st.markdown("### Formation elements")
    for eid in FORMATION_ELEMENT_IDS:
        result = element_results[eid]
        icon = "✅" if result["met"] else "❌"
        with st.expander(f"{icon} {ELEMENTS_BY_ID[eid]['name']}"):
            st.write(result["reason"])

    st.markdown("### Validity considerations")
    for element in CONTRACT_ELEMENTS:
        if element["category"] != "validity":
            continue
        result = element_results[element["id"]]
        icon = "✅" if result["met"] else "⚠️"
        with st.expander(f"{icon} {element['name']}"):
            st.write(result["reason"])

    # --- Follow-up question ---
    st.markdown("### Ask a follow-up question")
    follow_up = st.text_input("Your question about this analysis:")
    if st.button("Submit follow-up") and follow_up:
        with st.spinner("Thinking..."):
            answer = ask_follow_up(scenario_text, element_results, follow_up)
        st.session_state["chat_history"].append((follow_up, answer))

    for q, a in st.session_state["chat_history"]:
        st.markdown(f"**Q:** {q}")
        st.markdown(f"**A:** {a}")

    # --- Download as Word document ---
    docx_bytes = build_docx(scenario_text, contract_formed, element_results, ELEMENTS_BY_ID)
    st.download_button(
        label="Download analysis as Word document",
        data=docx_bytes,
        file_name="contract_formation_analysis.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )