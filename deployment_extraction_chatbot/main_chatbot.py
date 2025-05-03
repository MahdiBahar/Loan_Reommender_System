# main_chatbot.py

from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from extract_parameters_func import extract_parameters, VALID_CRITERIA
from filter_sort import get_query_params , load_record

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # restrict in prod
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)

# In-memory session store: session_id -> params dict
_sessions: Dict[str, Dict[str, Any]] = {}

# Request/response schemas
class ChatRequest(BaseModel):
    session_id: str
    text: str

class ChatResponse(BaseModel):
    session_id: str
    extracted_parameters_value: Dict[str, Optional[Any]]
    generated_message: str
    filter_results: str
    recom_button : bool = False

class SessionRequest(BaseModel):
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    sid = req.session_id

    # Initialize session if it doesn't exist
    if sid not in _sessions:
        _sessions[sid] = {k: None for k in VALID_CRITERIA}
    prior_params = _sessions[sid]

    # Extract parameters, merge into prior state, and build message
    updated_params, msg, rb = extract_parameters(req.text, prior_params)
    _records = load_record()
    results , msg_filter = get_query_params(
        _records,
        deposit__amount=updated_params.get("Deposit_amount"),
        repayment__duration=updated_params.get("Repayment_duration"),
        deposit__duration=updated_params.get("Deposit_duration"),
        interest__rate=updated_params.get("Interest_rate"),
        credit__score=updated_params.get("Credit_score"),
        loan__amount=updated_params.get("Loan_amount")
    )


    # Persist updated state
    _sessions[sid] = updated_params

    return ChatResponse(
        session_id=sid,
        extracted_parameters_value=updated_params,
        generated_message=msg,
        filter_results=msg_filter,
        recom_button= rb
    )

# @app.get("/close_session")
@app.post("/close_session")
async def close_session(req: SessionRequest):
    sid = req.session_id
    if sid in _sessions:
        del _sessions[sid]
        return {"status": "session closed"}
    raise HTTPException(status_code=404, detail="session not found")
