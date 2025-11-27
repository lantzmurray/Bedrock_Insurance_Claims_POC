# src/validators.py

import json

REQUIRED_FIELDS = [
    "claimant_name",
    "policy_number",
    "incident_date",
    "claim_amount",
    "incident_description",
]


def validate_extracted_info(raw_text: str) -> dict:
    """
    Try to parse the model output as JSON and ensure the required fields exist.
    If parsing fails, return a wrapper structure so we don't crash.
    """
    try:
        # Extract JSON from the raw text if it contains extra text
        import re
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
        else:
            data = json.loads(raw_text)
    except json.JSONDecodeError:
        # Model didn't return valid JSON; keep the raw output for debugging
        return {
            "claimant_name": None,
            "policy_number": None,
            "incident_date": None,
            "claim_amount": None,
            "incident_description": None,
            "raw_model_output": raw_text,
        }

    # Ensure required keys exist; if not, default to None
    if isinstance(data, dict):
        for field in REQUIRED_FIELDS:
            data.setdefault(field, None)
    else:
        # Unexpected format → wrap
        data = {
            "claimant_name": None,
            "policy_number": None,
            "incident_date": None,
            "claim_amount": None,
            "incident_description": None,
            "raw_model_output": raw_text,
        }

    return data
