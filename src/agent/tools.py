import os
import json
import logging
import re
from typing import Dict, List, Any, Optional
from src.agent.opensearch_client import OpenSearchClient

logger = logging.getLogger("scheme_finder.tools")

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "schemes.json")

def load_schemes() -> List[Dict[str, Any]]:
    """Load scheme records from local JSON database."""
    try:
        abs_path = os.path.abspath(DATA_PATH)
        if os.path.exists(abs_path):
            with open(abs_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading schemes from {DATA_PATH}: {e}")
    return []

# Initialize OpenSearch client
_opensearch = OpenSearchClient()
_all_schemes = load_schemes()
if _opensearch.is_connected and _all_schemes:
    _opensearch.index_schemes(_all_schemes)


def check_eligibility(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic rule engine matching user demographic parameters against schemes.json.
    
    user_profile params:
      - age (int)
      - income (float/int, annual in INR)
      - gender ('male', 'female', 'other', 'all')
      - occupation ('farmer', 'student', 'vendor', 'self_employed', 'unemployed', 'general', etc.)
      - state (str, e.g. 'West Bengal', 'Delhi', 'Maharashtra', 'all')
      - category (str, e.g. 'General', 'SC', 'ST', 'OBC', 'SECC_2011', 'BPL')
    """
    schemes = load_schemes()
    eligible_schemes = []
    ineligible_schemes = []

    user_age = user_profile.get("age")
    user_income = user_profile.get("income")
    user_gender = str(user_profile.get("gender", "")).strip().lower()
    user_occ = str(user_profile.get("occupation", "")).strip().lower()
    user_state = str(user_profile.get("state", "")).strip().lower()
    user_cat = str(user_profile.get("category", "")).strip().upper()

    for scheme in schemes:
        rules = scheme.get("eligibility", {})
        reasons = []

        # Age check
        if user_age is not None and isinstance(user_age, (int, float)):
            min_age = rules.get("min_age", 0)
            max_age = rules.get("max_age", 120)
            if not (min_age <= user_age <= max_age):
                reasons.append(f"Age {user_age} is outside eligible range ({min_age}-{max_age} years).")

        # Income check
        if user_income is not None and isinstance(user_income, (int, float)):
            max_inc = rules.get("max_income")
            if max_inc is not None and user_income > max_inc:
                reasons.append(f"Annual income ₹{user_income:,.0f} exceeds max ceiling ₹{max_inc:,.0f}.")

        # Gender check
        scheme_gender = str(rules.get("gender", "all")).lower()
        if user_gender and scheme_gender != "all" and user_gender != scheme_gender:
            reasons.append(f"Scheme is restricted to {scheme_gender} applicants.")

        # Occupation check
        allowed_occs = [str(o).lower() for o in rules.get("occupations", ["all"])]
        if user_occ and "all" not in allowed_occs:
            if not any(occ_term in user_occ or user_occ in occ_term for occ_term in allowed_occs):
                reasons.append(f"Target occupations ({', '.join(allowed_occs)}) do not match '{user_occ}'.")

        # State check
        allowed_states = [str(s).lower() for s in rules.get("states", ["all"])]
        if user_state and "all" not in allowed_states:
            if not any(st in user_state or user_state in st for st in allowed_states):
                reasons.append(f"Scheme is restricted to residents of {', '.join(allowed_states).title()}.")

        # Category check
        allowed_cats = [str(c).upper() for c in rules.get("categories", ["ALL"])]
        if user_cat and "ALL" not in allowed_cats and user_cat not in allowed_cats:
            reasons.append(f"Category '{user_cat}' is not in scheme eligible groups ({', '.join(allowed_cats)}).")

        summary_item = {
            "id": scheme["id"],
            "name": scheme["name"],
            "category": scheme["category"],
            "objective": scheme["objective"],
            "benefits": scheme["benefits"],
            "apply_link": scheme["apply_link"],
            "documents": scheme["documents"]
        }

        if not reasons:
            summary_item["eligible"] = True
            eligible_schemes.append(summary_item)
        else:
            summary_item["eligible"] = False
            summary_item["reasons"] = reasons
            ineligible_schemes.append(summary_item)

    return {
        "status": "success",
        "total_evaluated": len(schemes),
        "eligible_count": len(eligible_schemes),
        "eligible_schemes": eligible_schemes,
        "ineligible_schemes": ineligible_schemes
    }


def get_scheme_details(scheme_id: str) -> Dict[str, Any]:
    """Retrieve full scheme specifications, required docs, and official application URL."""
    schemes = load_schemes()
    target_id = str(scheme_id).strip().lower()

    for scheme in schemes:
        if scheme["id"].lower() == target_id or target_id in scheme["id"].lower():
            return {
                "status": "success",
                "scheme": scheme
            }
    
    # Try name match
    for scheme in schemes:
        for lang_name in scheme["name"].values():
            if target_id in lang_name.lower():
                return {
                    "status": "success",
                    "scheme": scheme
                }

    return {
        "status": "not_found",
        "message": f"Scheme with ID or name matching '{scheme_id}' was not found.",
        "available_schemes": [s["id"] for s in schemes]
    }


def search_schemes(query: str) -> List[Dict[str, Any]]:
    """
    Free-text search over government schemes.
    Queries OpenSearch container if online; otherwise executes keyword & fuzzy matching fallback.
    """
    query_clean = query.strip().lower()
    if not query_clean:
        return load_schemes()

    # Try OpenSearch container first
    opensearch_results = _opensearch.search(query)
    if opensearch_results is not None:
        return opensearch_results

    # Fallback local fuzzy/keyword scoring search
    schemes = load_schemes()
    query_tokens = re.findall(r'\w+', query_clean)
    scored_results = []

    for scheme in schemes:
        score = 0
        # Check in names across all languages
        for lang, name in scheme["name"].items():
            name_lower = name.lower()
            if query_clean in name_lower:
                score += 10
            for token in query_tokens:
                if token in name_lower:
                    score += 3

        # Check in objective
        for lang, obj in scheme["objective"].items():
            obj_lower = obj.lower()
            for token in query_tokens:
                if token in obj_lower:
                    score += 2

        # Check category
        if query_clean in scheme["category"].lower():
            score += 5

        # Check benefits
        for lang, ben in scheme["benefits"].items():
            ben_lower = ben.lower()
            for token in query_tokens:
                if token in ben_lower:
                    score += 1

        # Check documents
        for doc in scheme.get("documents", []):
            if any(token in doc.lower() for token in query_tokens):
                score += 1

        if score > 0:
            scored_results.append((score, scheme))

    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_results]
