from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from starlette.responses import Response

import os
import time
from pathlib import Path

from backend.app.api import ws_chat, documents, rag, chat, metrics, admin ,auth

app = FastAPI(title="ELARA AI Chatbot : Chat With Your Data")

# Get the root directory (one level up from backend/)
BASE_DIR = Path(__file__).parent.parent.parent

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware to measure request time and record metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Record metrics using function from metrics.py
    try:
        from backend.app.api.metrics import record_request
        route_path = request.url.path
        method = request.method
        status_code = response.status_code
        record_request(
            method=method,
            endpoint=route_path,
            status_code=status_code,
            latency=process_time,
            error=(status_code >= 400)
        )
    except ImportError:
        pass

    return response

app.mount("/frontend", StaticFiles(directory=BASE_DIR / "frontend"), name="frontend")

@app.get("/")
async def serve_index():
    return FileResponse(BASE_DIR / "frontend/index.html")

@app.get("/chat")
async def serve_chat():
    return FileResponse(BASE_DIR / "frontend/chat.html")

@app.get("/admin")
async def serve_admin():
    return FileResponse(BASE_DIR / "frontend/admin.html")


# Include all routers
app.include_router(ws_chat.router)
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(admin.router)
app.include_router(metrics.router)
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# app.include_router(rag.router, prefix="/rag", tags=["RAG"])
# app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "ELARA AI Chatbot is running"}