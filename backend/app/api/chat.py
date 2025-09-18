# Non-RAG chat API

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.services.chat_service import get_openrouter_response

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat_config(request: ChatRequest):
    try:
        ai_reply = await get_openrouter_response(request.message)
        return ChatResponse(reply=ai_reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error from OpenRouter API: {str(e)}")

