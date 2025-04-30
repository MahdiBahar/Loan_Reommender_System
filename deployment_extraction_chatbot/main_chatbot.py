# main_chatbot.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, Optional

from extract_parameters_func import extract_parameters

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    text: str

class ChatResponse(BaseModel):
    extracted_parameters_value: Dict[str, Optional[Any]]
    generated_message: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    input_text = req.text
    new_params, msg = extract_parameters(input_text)
    if not msg:
        raise HTTPException(status_code=400, detail="No response generated")

    return ChatResponse(
        extracted_parameters_value=new_params,
        generated_message=msg
    )
