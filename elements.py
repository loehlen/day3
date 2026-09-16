# elements.py
# This file just holds DATA — no logic, no Streamlit code. It describes
# the six elements of contract formation/validity, and for each one,
# exactly which facts we need to extract from the contract text to
# assess it. Based on:
# https://www.thelawhandbook.org.au/71-how-contract-law-works/elements-of-a-contract-2xw6m-lxpbe
#
# "category" separates the two groups:
#   - "formation": needed for a contract to exist at all
#   - "validity": affects whether an already-formed contract is enforceable

CONTRACT_ELEMENTS = [
    {
        "id": "offer_acceptance",
        "name": "Offer and Acceptance",
        "category": "formation",
        # A short, plain-English description of the element, used later
        # to find the most relevant chunk of the contract for this element.
        "query": "an offer being made by one party and accepted by the other party",
        "facts_needed": [
            "offer_made",
            "offer_definite",              # essential terms (price, subject matter) settled?
            "offer_communicated",
            "offer_withdrawn_before_acceptance",  # was it withdrawn before acceptance occurred?
            "acceptance_given",
            "acceptance_mirrors_offer",    # or was it a counter-offer instead?
            "acceptance_communicated",
        ],
    },
    {
        "id": "intention",
        "name": "Intention to Create Legal Relations",
        "category": "formation",
        "query": "whether the parties intended to be legally bound by this agreement",
        "facts_needed": [
            "relationship_type",
            "commercial_context",
            "express_intention_stated",
        ],
    },
    {
        "id": "consideration",
        "name": "Consideration",
        "category": "formation",
        "query": "payment, price, or something of value exchanged between the parties",
        "facts_needed": [
            "consideration_present",
            "consideration_has_value",
            "consideration_is_past",
            "is_deed",
        ],
    },
    {
        "id": "capacity",
        "name": "Legal Capacity",
        "category": "formation",
        "query": "the age, mental state, or legal status of the parties entering the contract",
        "facts_needed": [
            "all_parties_adults",
            "mental_impairment_indicated",
            "corporate_party_authorised",
            "bankrupt_party_involved",
        ],
    },
    {
        "id": "consent",
        "name": "Consent",
        "category": "validity",
        "query": "any mistake, misrepresentation, pressure, or unfair terms affecting the parties' agreement",
        "facts_needed": [
            "mistake_indicated",
            "misrepresentation_indicated",
            "duress_indicated",
            "undue_influence_indicated",
            "standard_form_contract",
        ],
    },
    {
        "id": "legality",
        "name": "Legality",
        "category": "validity",
        "query": "whether the subject matter of the contract is lawful",
        "facts_needed": [
            "subject_matter_illegal",
            "against_public_policy",
        ],
    },
]

# A quick lookup by id, and separate lists for the two categories —
# other files will use these instead of looping through everything
# themselves each time.
ELEMENTS_BY_ID = {el["id"]: el for el in CONTRACT_ELEMENTS}
FORMATION_ELEMENT_IDS = [el["id"] for el in CONTRACT_ELEMENTS if el["category"] == "formation"]
VALIDITY_ELEMENT_IDS = [el["id"] for el in CONTRACT_ELEMENTS if el["category"] == "validity"]