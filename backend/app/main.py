from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
import time

from backend.app.api import ws_chat, documents, rag, chat, metrics ,admin

app = FastAPI(title="ELARA AI Chatbot")

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
        # Import here to avoid circular import on startup
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
        # Logging can be added here if needed
        pass

    return response

# Include all routers
app.include_router(ws_chat.router)
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(admin.router)

app.include_router(rag.router, prefix="/rag", tags=["RAG"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(metrics.router)
# , prefix="/metrics", tags=["Metrics"]


@app.get("/")
async def root():
    return {"message": "Hello, ELARA!"}
