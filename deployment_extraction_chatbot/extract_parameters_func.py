# extract_parameters_func.py
from typing import Any, Dict, Tuple
from datetime import datetime, timedelta

from LLM_parser_func import clean_and_parse
from LLM_model import extract_chain
from random_responses import (
    random_response_summary,
    random_invite,
    random_irrelevant,
    random_invalid,
    random_loan_field,
)

# 1) Validation rules, labels & suffixes
VALID_CRITERIA = {
    "deposit_amount": None,
    "deposit_duration": [1, 2, 3, 4, 6, 12],
    "loan_amount": lambda x: x <= 300_000_000,
    "Credit_score": ["A", "B", "C", "D", "E", None],
    "repayment_duration": [12, 24, 36, 48, 60],
    "Interest_rate": [4, 14, 18, 23],
    "Loan_field": None,
}

LABELS = {
    "deposit_amount": "مقدار سپرده",
    "loan_amount": "مقدار وام",
    "deposit_duration": "مدت سپرده",
    "repayment_duration": "دوره بازپرداخت",
    "Credit_score": "رتبه اعتباری",
    "Interest_rate": "نرخ سود",
    "Loan_field": "",
}

SUFFIXES = {
    "deposit_amount": " تومان",
    "loan_amount": " تومان",
    "deposit_duration": " ماه",
    "repayment_duration": " ماه",
    "Credit_score": "",
    "Interest_rate": " درصد",
    "Loan_field": "",
}


# Initialize chain once at import
extraction_chain = extract_chain()


def format_params_message(params: Dict[str, Any]) -> str:
    """
    Build a human-readable summary of all non-None parameters.
    """
    lines = []
    for key in (
        "deposit_amount",
        "loan_amount",
        "deposit_duration",
        "repayment_duration",
        "Credit_score",
        "Interest_rate",
    ):
        val = params.get(key)
        if val is not None:
            lines.append(f" {LABELS[key]}: {val}{SUFFIXES[key]}")
    if not lines:
        return "هنوز مقادیری دریافت نکردم."
    return "\n".join(lines) + "\n\n" + random_invite()



def extract_parameters(
    user_input: str,
    prior_params: Dict[str, Any]
) -> Tuple[Dict[str, Any], str]:
    """
    Extract new parameter values from user_input, merge into prior_params,
    and generate an appropriate response message.
    """
    # rb = False
    fallback = prior_params.copy()
    # Try extraction
    try:
        raw = extraction_chain.predict(user_input=user_input)
        new_params = clean_and_parse(raw)
    except Exception:
        # If parsing fails, return fallback
        # fallback = {k: None for k in VALID_CRITERIA}
        
        return fallback, random_irrelevant() , False

    # Determine template-based response and collect valid updates
    valid_updates: Dict[str, Any] = {}
    invalid_msgs = []
    invalid_keys = []
    # Template logic for raw message
    if new_params.get("Loan_field") and all(
        new_params.get(k) is None for k in new_params if k != "Loan_field"
    ):
        raw_msg = random_loan_field()
        rb = False
    elif not any(v is not None for v in new_params.values()):
        raw_msg = random_irrelevant()
        rb = False
    else:
        # Validate each extracted value
        for k, v in new_params.items():
            if k == "Loan_field" or v is None:
                continue
            crit = VALID_CRITERIA[k]
            ok, hint = True, None
            if isinstance(crit, list) and v not in crit:
                ok, hint = False, ", ".join(str(x) for x in crit if x is not None)
            if callable(crit) and not crit(v):
                ok, hint = False, "مقدار وام،کوچکتر یا مساوی ۳۰۰ میلون تومن هست."
            if ok:
                valid_updates[k] = v
            else:
                invalid_keys.append(k)
                invalid_msgs.append(
                    random_invalid(LABELS[k])
                    + (f"\nراهنمایی: {hint}" if hint else "")
                )

          # Merge prior state with valid updates
    updated_params = prior_params.copy()
    for k, v in valid_updates.items():
        updated_params[k] = v

        # Case: only invalid
    if not valid_updates and invalid_keys:
        msg = "\n".join(invalid_msgs)
        rb = False

        # Case: only valid
    elif valid_updates and not invalid_keys:
        msg = random_response_summary(format_params_message(updated_params))
        rb = True

    elif valid_updates and invalid_keys:
        raw_msg_invalid = "\n".join(invalid_msgs)
        raw_msg_valid = random_response_summary(format_params_message(updated_params))
        msg = f"{raw_msg_invalid}\n\n{raw_msg_valid}"
        rb = True
    else:
        # No updates: use the template-based reply
        msg = raw_msg
        rb = False
    return updated_params, msg, rb
