# main_chatbot.py

import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from extract_parameters_func import extract_parameters, VALID_CRITERIA


_sessions: Dict[str, Dict[str, Any]] = {}


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    text: str

class ChatResponse(BaseModel):
    session_id: str
    extracted_parameters_value: Dict[str, Optional[Any]]
    generated_message: str

# class SessionRequest(BaseModel):
#     session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    sid = req.session_id

    # 3a) initialize this session if it doesn't exist
    if sid not in _sessions:
        _sessions[sid] = {k: None for k in VALID_CRITERIA}

    # 3b) fetch the last‐seen params
    session_params = _sessions[sid]

    # 3c) extract new values and decide on a message
    new_params, msg = extract_parameters(req.text)

    # 3d) overwrite only the keys the user just supplied
    for k, v in new_params.items():
        if v is not None:
            session_params[k] = v

    # 3e) save back into our store
    _sessions[sid] = session_params

    return ChatResponse(
        session_id=sid,
        extracted_parameters_value=session_params,
        generated_message=msg
    )


# @app.get("/close_session")
# @app.post("/close_session")
# async def close_session(req: SessionRequest):
#     sid = req.session_id
#     if sid in _sessions:
#         del _sessions[sid]
#         return {"status": "session closed"}
#     raise HTTPException(status_code=404, detail="session not found")