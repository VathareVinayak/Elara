from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Optional

from backend.app.db.crud import create_session, get_session, create_message, get_messages_by_session
from backend.app.core.rag_pipeline import rag_answer  # RAG pipeline async function

router = APIRouter()

async def send_chat_history(websocket: WebSocket, session_id: str):
    messages = await get_messages_by_session(session_id)
    history = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    await websocket.send_json({"type": "history", "messages": history})

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, session_id: Optional[str] = None):
    await websocket.accept()

    if session_id:
        existing_session = await get_session(session_id)
        if not existing_session:
            await websocket.send_json({"error": "Session not found"})
            await websocket.close()
            return
    else:
        session_id = await create_session()

    # Send the created or existing session_id back to client
    await websocket.send_json({"type": "session_start", "session_id": session_id})

    await send_chat_history(websocket, session_id)

    try:
        while True:
            data = await websocket.receive_json()
            user_query = data.get("query")
            if not user_query:
                await websocket.send_json({"error": "No query provided"})
                continue

            await create_message(session_id=session_id, content=user_query, role="user")
            assistant_response = await rag_answer(user_query, session_id=session_id)
            await create_message(session_id=session_id, content=assistant_response, role="assistant")

            await websocket.send_json({
                "type": "assistant_message",
                "content": assistant_response,
                "session_id": session_id
            })
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session {session_id}")
