# RAG chat API
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.rag_pipeline import rag_answer

router = APIRouter()

class RagChatRequest(BaseModel):
    query: str

class RagChatResponse(BaseModel):
    answer: str

@router.post("/chat", response_model=RagChatResponse)
async def rag_chat(request: RagChatRequest):
    answer = await rag_answer(request.query)
    return RagChatResponse(answer=answer)