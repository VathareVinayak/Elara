from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional

from backend.app.db.crud import create_session , create_message , create_document
from backend.app.db.crud import get_session,get_messages_by_session,get_all_sessions

from backend.app.core.rag_pipeline import rag_answer

from backend.app.tools.math_tools import calculate
from backend.app.tools.date_tools import date_diff

import logging
import re


router = APIRouter()
logger = logging.getLogger(__name__)

def is_math_query(query: str) -> bool:
    query_l = query.lower()
    return (
        bool(re.match(r'^[\d\+\-*/\(\)\.\s\^%]+$', query_l))
        or any(key in query_l for key in [
            "calculate", "compute", "equation", "solve", "derivative",
            "differentiate", "d/dx", "root", "solution", "trig", "sin", "cos", "tan", "angle"
        ])
        or ('=' in query_l and re.search(r'[a-zA-Z]', query_l))
    )

def is_date_query(query: str) -> bool:
    ql = query.lower()
    return (
        "days between" in ql
        or "difference between dates" in ql
        or len(re.findall(r"\d{4}-\d{2}-\d{2}", query)) >= 2
    )

async def send_chat_history(websocket: WebSocket, session_id: str):
    messages = await get_messages_by_session(session_id)
    history = [{"role": m["role"], "content": m["content"]} for m in messages]
    await websocket.send_json({"type": "history", "messages": history, "session_id": session_id})
    logger.info(f"Sent chat history for session {session_id}")

async def send_all_sessions(websocket: WebSocket):
    sessions = await get_all_sessions()
    session_list = [{"id": s["id"], "created_at": s.get("created_at"), "status": s.get("status")} for s in sessions]
    await websocket.send_json({"type": "sessions_list", "sessions": session_list})
    logger.info("Sent all sessions list to client")

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
        # If no session_id is passed, create a new session in DB
        session_id = await create_session()
        logger.info(f"Created new session: {session_id}")

    # Notify user about session start and send trecent chat history
    await websocket.send_json({"type": "session_start", "session_id": session_id})
    await send_chat_history(websocket, session_id)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "get_sessions":
                await send_all_sessions(websocket)

            elif msg_type == "select_session":
                selected_session_id = data.get("session_id")
                
                if selected_session_id:
                    # Load history of the selected session
                    await send_chat_history(websocket, selected_session_id)
                else:
                    await websocket.send_json({"error": "No session_id provided for select_session"})

            elif msg_type == "query":
                user_query = data.get("query")
                if not user_query:
                    logger.warning(f"No query provided by session {session_id}")
                    await websocket.send_json({"error": "No query provided"})
                    continue

                logger.info(f"Received query for session {session_id}: {user_query}")
                await create_message(session_id=session_id, content=user_query, role="user")

                tool_response = None
                # Check if query matches math pattern
                if is_math_query(user_query):
                    tool_response = calculate(user_query)
                    
                # Check if query is a date difference type
                elif is_date_query(user_query):
                    dates = re.findall(r"\d{4}-\d{2}-\d{2}", user_query)
                    if len(dates) >= 2:
                        tool_response = date_diff(dates[0], dates[1])

                if tool_response:
                    # Send tools response (math/date) instead of RAG-Pipeline
                    await create_message(session_id=session_id, content=tool_response, role="assistant")
                    await websocket.send_json({
                        "type": "assistant_message",
                        "content": tool_response,
                        "session_id": session_id
                    })
                    logger.info(f"Sent tool response to session {session_id}")
                    continue
                
                # Sent request to the RAG    
                assistant_response = await rag_answer(user_query, session_id=session_id)
                await create_message(session_id=session_id, content=assistant_response, role="assistant")
                logger.info(f"Sent assistant response to session {session_id}")
                await websocket.send_json(
                    {
                        "type": "assistant_message",
                        "content": assistant_response,
                        "session_id": session_id
                    })

            else:
                await websocket.send_json({"error": f"Unknown message type: {msg_type}"})
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket: {e}")
        await websocket.send_json({"error": "Internal server error"})
