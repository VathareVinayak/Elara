from fastapi import FastAPI
from app.api import chat, documents ,rag  
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager



app = FastAPI(title="ELARA AI Chatbot")

# Routers Registration
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(rag.router, prefix="/rag", tags=["RAG"]) 

@app.on_event("startup")
async def startup_event():
    print("Starting ELARA backend app...")


@app.get("/")
async def root():
    return {"message": "Hello, ELARA!"}



