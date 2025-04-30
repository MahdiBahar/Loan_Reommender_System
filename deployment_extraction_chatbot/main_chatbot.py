# main_chatbot.py

import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from extract_parameters_func import extract_parameters, VALID_CRITERIA

app = FastAPI()

# 1) Add session middleware with a secret key
app.add_middleware(SessionMiddleware, secret_key="YOUR_RANDOM_SECRET")

# 2) CORS so your frontend can reach it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # lock this down in production!
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    text: str

class ChatResponse(BaseModel):
    extracted_parameters_value: Dict[str, Optional[Any]]
    generated_message: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    # 3) Initialize a session ID (if new) so we can track per-user state
    if "session_id" not in request.session:
        request.session["session_id"] = str(uuid.uuid4())
        # start with all-None parameters
        request.session["params"] = {k: None for k in VALID_CRITERIA}

    # 4) Pull prior state
    session_params: Dict[str, Any] = request.session["params"]

    # 5) Extract new values and template message
    new_params, msg = extract_parameters(req.text)

    # 6) Overwrite only those keys where user just provided a non-None value
    for k, v in new_params.items():
        if v is not None:
            session_params[k] = v

    # 7) Persist the updated state
    request.session["params"] = session_params

    # 8) Return the merged state + message
    return ChatResponse(
        extracted_parameters_value=session_params,
        generated_message=msg
    )
