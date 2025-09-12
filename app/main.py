from fastapi import FastAPI
from app.api import chat, documents


app = FastAPI(title="ELARA AI Chatbot")



@app.get("/")
async def root():
    return {"message": "Hello, ELARA!"}



