from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Optional
import logging

from backend.app.db.crud import create_session, get_session, create_message, get_messages_by_session
from backend.app.core.rag_pipeline import rag_answer  
router = APIRouter()
logger = logging.getLogger(__name__)

async def send_chat_history(websocket: WebSocket, session_id: str):
    messages = await get_messages_by_session(session_id)
    history = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    await websocket.send_json({"type": "history", "messages": history})
    logger.info(f"Sent chat history for session {session_id}")

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, session_id: Optional[str] = None):
    await websocket.accept()
    logger.info(f"WebSocket connection accepted, session_id={session_id}")

    if session_id:
        existing_session = await get_session(session_id)
        if not existing_session:
            logger.warning(f"Session not found: {session_id}")
            await websocket.send_json({"error": "Session not found"})
            await websocket.close()
            return
    else:
        session_id = await create_session()
        logger.info(f"Created new session: {session_id}")

    await websocket.send_json({"type": "session_start", "session_id": session_id})
    await send_chat_history(websocket, session_id)

    try:
        while True:
            data = await websocket.receive_json()
            user_query = data.get("query")
            if not user_query:
                logger.warning(f"No query provided by session {session_id}")
                await websocket.send_json({"error": "No query provided"})
                continue

            logger.info(f"Received query for session {session_id}: {user_query}")
            await create_message(session_id=session_id, content=user_query, role="user")
            assistant_response = await rag_answer(user_query, session_id=session_id)
            await create_message(session_id=session_id, content=assistant_response, role="assistant")
            logger.info(f"Sent assistant response to session {session_id}")

            await websocket.send_json({
                "type": "assistant_message",
                "content": assistant_response,
                "session_id": session_id
            })
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
