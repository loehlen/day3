"""
The if/then rule engine — this is where the actual legal reasoning
happens, in code you control, NOT inside the AI. Each function takes
the facts extracted in Step 9 and returns a verdict: whether the
element is met, and why.
"""

def evaluate_offer_acceptance(facts: dict) -> dict:
    if facts.get("offer_made") != True or facts.get("offer_definite") != True:
        return {"met": False, "reason": "No definite offer was made — essential terms were not settled, or this reads as mere willingness to negotiate rather than a binding offer."}
    if facts.get("offer_withdrawn_before_acceptance") == True:
        return {"met": False, "reason": "The offer appears to have been withdrawn before it was accepted."}
    if facts.get("offer_communicated") != True:
        return {"met": False, "reason": "The offer was not clearly communicated to the offeree."}
    if facts.get("acceptance_given") != True:
        return {"met": False, "reason": "No acceptance of the offer occurred."}
    if facts.get("acceptance_mirrors_offer") != True:
        return {"met": False, "reason": "The response does not mirror the offer exactly — this reads as a counter-offer, not acceptance."}
    if facts.get("acceptance_communicated") != True:
        return {"met": False, "reason": "Acceptance was not communicated back to the offeror."}
    return {"met": True, "reason": "A definite offer was made, communicated, and met with unequivocal, communicated acceptance."}


def evaluate_intention(facts: dict) -> dict:
    if facts.get("express_intention_stated") == True:
        return {"met": True, "reason": "The parties expressly stated their intention to be legally bound."}
    if facts.get("relationship_type") == "commercial" or facts.get("commercial_context") == True:
        return {"met": True, "reason": "This is an arm's-length commercial arrangement, so intention to create legal relations is presumed."}
    if facts.get("relationship_type") == "domestic_or_social":
        return {"met": False, "reason": "This reads as a domestic or social arrangement, where intention to create legal relations is presumed NOT to exist unless clearly stated otherwise."}
    return {"met": False, "reason": "Not enough information to determine the nature of the relationship or context between the parties."}


def evaluate_consideration(facts: dict) -> dict:
    if facts.get("is_deed") == True:
        return {"met": True, "reason": "Executed as a deed — consideration is not required for a binding agreement."}
    if facts.get("consideration_present") != True:
        return {"met": False, "reason": "No consideration (something of value) appears to have passed between the parties."}
    if facts.get("consideration_is_past") == True:
        return {"met": False, "reason": "The consideration appears to be 'past consideration' — already given before the promise was made — which is not valid consideration."}
    if facts.get("consideration_has_value") != True:
        return {"met": False, "reason": "The consideration does not appear to have real value (e.g. love/affection or a voluntary gift is not valid consideration)."}
    return {"met": True, "reason": "Valid consideration of real value passed between the parties."}


def evaluate_capacity(facts: dict) -> dict:
    if facts.get("all_parties_adults") == False:
        return {"met": False, "reason": "At least one party appears to be a minor — capacity may be limited to contracts for necessaries."}
    if facts.get("mental_impairment_indicated") == True:
        return {"met": False, "reason": "A mental impairment affecting a party's capacity to understand the contract is indicated."}
    if facts.get("corporate_party_authorised") == False:
        return {"met": False, "reason": "A corporate party's signatory does not appear to have had authority to bind the company."}
    return {"met": True, "reason": "No indication of a capacity issue affecting the parties."}


def evaluate_consent(facts: dict) -> dict:
    problems = []
    if facts.get("mistake_indicated") == True:
        problems.append("a possible mistake going to the basis of the agreement")
    if facts.get("misrepresentation_indicated") == True:
        problems.append("a possible misrepresentation inducing entry into the contract")
    if facts.get("duress_indicated") == True:
        problems.append("possible duress")
    if facts.get("undue_influence_indicated") == True:
        problems.append("possible undue influence")
    if problems:
        return {"met": False, "reason": "Genuine consent may be affected by: " + "; ".join(problems) + "."}
    if facts.get("standard_form_contract") == True:
        return {"met": True, "reason": "No vitiating factor indicated, though this is a standard form contract — unfair contract terms under the ACL may still be worth checking separately."}
    return {"met": True, "reason": "No indication of a factor affecting genuine consent."}


def evaluate_legality(facts: dict) -> dict:
    if facts.get("subject_matter_illegal") == True:
        return {"met": False, "reason": "The subject matter of the contract appears to be illegal."}
    if facts.get("against_public_policy") == True:
        return {"met": False, "reason": "The contract appears to be contrary to public policy (e.g. restraint of trade, ousting court jurisdiction)."}
    return {"met": True, "reason": "No indication that the contract is illegal or contrary to public policy."}


# Maps each element's id to its rule function, so the orchestrator can
# just look up the right function instead of a long if/elif chain.
RULE_FUNCTIONS = {
    "offer_acceptance": evaluate_offer_acceptance,
    "intention": evaluate_intention,
    "consideration": evaluate_consideration,
    "capacity": evaluate_capacity,
    "consent": evaluate_consent,
    "legality": evaluate_legality,
}