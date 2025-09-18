from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import ws_chat, documents, rag, chat

app = FastAPI(title="ELARA AI Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_chat.router)
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(rag.router, prefix="/rag", tags=["RAG"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "Hello, ELARA!"}
