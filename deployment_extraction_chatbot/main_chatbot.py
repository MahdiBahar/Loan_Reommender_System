# main_chatbot.py

from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from extract_parameters_func import extract_parameters, VALID_CRITERIA
from LLM_parser_func import clean_and_parse
from LLM_model import extract_chain

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)

LABELS = {
    "deposit_amount": "مقدار سپرده",
    "loan_amount": "مقدار وام",
    "deposit_duration": "مدت سپرده",
    "repayment_duration": "دوره بازپرداخت",
    "Credit_score": "رتبه اعتباری",
    "Interest_rate": "نرخ سود",
    "Loan_field": "",
    "hello_msg" : ""
}

SUFFIXES = {
    "deposit_amount": " تومان",
    "loan_amount": " تومان",
    "deposit_duration": " ماه",
    "repayment_duration": " ماه",
    "Credit_score": "",
    "Interest_rate": " درصد",
    "Loan_field": "",
    "hello_msg" : ""
}

SUFFIXES_PERSIAN = {
    "مقدار سپرده": "تومن",
    "مقدار وام": "تومن",
    "مدت سپرده": "ماه",
    "دوره بازپرداخت": "ماه",
    "رتبه اعتباری": "",
    "نرخ سود": "درصد",
}

# In-memory session store
# session_id -> { params, last_user_msg, last_raw_params }
_sessions: Dict[str, Dict[str, Any]] = {}
#build parser chain for raw detection
parser_chain = extract_chain()

class ChatRequest(BaseModel):
    session_id: str
    text: str

class ChatResponse(BaseModel):
    session_id: str
    extracted_parameters_value: Dict[str, Optional[Any]]
    generated_message: list
    filter_results: Dict
    recom_button : bool = False
    combined  : Optional[str] = None
    is_fallback: bool = False

class SessionRequest(BaseModel):
    session_id: str

@app.post("/chatbot", response_model=ChatResponse)
async def chat(req: ChatRequest):
    sid = req.session_id
    user_text = req.text.strip()
    # Only track the six main parameters (exclude Loan_field)
    filtered_keys = [k for k in VALID_CRITERIA if k != "Loan_field" and k != "hello_msg"]
    # Initialize session if missing
    if sid not in _sessions:
        
        _sessions[sid] = {
            "params": {k: None for k in VALID_CRITERIA},
            "last_user_msg": "",
            "last_raw_params": {k: None for k in filtered_keys},
            "invalid_keys" : []
        }
    entry = _sessions[sid]
    prior_params = entry["params"]
    prev_msg = entry["last_user_msg"]
    last_raw = entry["last_raw_params"]
    inv_key = entry["invalid_keys"]

    # First-pass parse raw user text, with fallback on parse errors
    raw1 = parser_chain.predict(user_input=user_text)
    try:
        parsed = clean_and_parse(raw1)
    except Exception:
        parsed = {k: None for k in VALID_CRITERIA}
    # Filter to six parameters
    new_raw = {k: parsed.get(k) for k in prior_params.keys()}
    new_raw_params = {k: parsed.get(k) for k in filtered_keys}
    # Determine fallback: no extraction AND last turn had exactly one raw param
    one_last = sum(1 for v in last_raw.values() if v is not None) == 1
    no_new_list = [v is not None for v in new_raw_params.values()]
    no_new = not any(v is not None for v in new_raw_params.values())
    short_input = len(user_text.split()) <= 4
    is_fallback = (no_new and one_last) and short_input
    invalid_len_check = len(inv_key)>=1
    is_fallback_invalid = no_new and invalid_len_check and short_input

    combined = None  # Ensure combined is always defined

     # DEBUG: log internal state
    print(f"DEBUG [{sid}]: one_last={one_last}, no_new={no_new}, short_input={short_input}")
    print(f"DEBUG [{sid}]: no_new_list={no_new_list}")
    print(f"DEBUG [{sid}]: last_raw={last_raw}")
    print(f"DEBUG [{sid}]: new_raw={new_raw}")
    print(f"DEBUG [{sid}]: new_raw_params={new_raw_params}")
    print(f"DEBUG [{sid}]: invalid_key={inv_key}")
    print(f"DEBUG [{sid}]: invalid_key_validation={is_fallback_invalid}")
    if (is_fallback or is_fallback_invalid ) and prev_msg:
        # build combined input: only the single parameter phrase from last turn + current text
        label = ""  # Ensure label is always defined
        if is_fallback and not is_fallback_invalid:
        
            key = next(k for k, v in last_raw.items() if v is not None)

            label = LABELS.get(key, key)

        elif (not is_fallback and is_fallback_invalid) or ( is_fallback and is_fallback_invalid):
            
            label = inv_key[0] if inv_key else ""

        safe_label = label if isinstance(label, str) and label else ""
        combined = f"{safe_label} {user_text} {SUFFIXES_PERSIAN.get(safe_label, '')}".strip()
        print(f"DEBUG [{sid}]: combined={combined}")
        # rerun extraction chain on combined text
        raw2 = parser_chain.predict(user_input=combined)
        try:
            new_raw = clean_and_parse(raw2)
        except Exception:
            new_raw = {k: None for k in VALID_CRITERIA}
        # extract parameters from the combined text
        # now extract with combined text
        updated_params, msg, rb, first_result, invalid_key = extract_parameters(combined, prior_params, new_raw)
    else:
        # normal extraction
        result = extract_parameters(user_text, prior_params, new_raw)
        try:
            if result is not None and isinstance(result, tuple):
                if isinstance(result, (list, tuple)) and len(result) == 5:
                    updated_params, msg, rb, first_result, invalid_key = result
                else:
                    updated_params = {k: None for k in prior_params.keys()}
                    msg = "خطا در استخراج پارامترها"
                    rb = None
                    first_result = None
                    invalid_key = []
            else:
                # Handle the case where result is not iterable (e.g., None or unexpected type)
                updated_params = {k: None for k in prior_params.keys()}
                msg = "خطا در استخراج پارامترها"
                rb = None
                first_result = None
                invalid_key = []
        except Exception:
            updated_params = {k: None for k in prior_params.keys()}
            msg = "خطا در استخراج پارامترها"
            rb = None
            first_result = None
            invalid_key = []

    # Persist state
    entry["params"] = updated_params
    entry["last_user_msg"] = user_text
    entry["last_raw_params"] = {k: new_raw.get(k) for k in filtered_keys}
    entry["invalid_keys"] = invalid_key
    return ChatResponse(
        session_id=sid,
        extracted_parameters_value=updated_params,
        generated_message=[msg] if isinstance(msg, str) else msg,
        filter_results=first_result if first_result is not None else {},
        recom_button= bool(rb),
        is_fallback=is_fallback,
        combined=combined if is_fallback else None,
    )

@app.post("/close_session")
async def close_session(req: SessionRequest):
    sid = req.session_id
    if sid in _sessions:
        del _sessions[sid]
        return {"status": "session closed"}
    raise HTTPException(status_code=404, detail="session not found")
