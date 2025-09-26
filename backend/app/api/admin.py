from fastapi import APIRouter, HTTPException
from typing import List

from backend.app.db.crud import get_all_sessions,get_messages_by_session,get_documents_by_session
from backend.app.db.crud import delete_session,delete_message,delete_document


router = APIRouter()

# List all sessions
@router.get("/admin/sessions")
async def list_sessions():
    try:
        sessions = await get_all_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# List messages for a session
@router.get("/admin/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    try:
        messages = await get_messages_by_session(session_id)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# List documents for a session
@router.get("/admin/sessions/{session_id}/documents")
async def get_session_documents(session_id: str):
    try:
        documents = await get_documents_by_session(session_id)
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Delete a session by ID (cascades deleting related messages/documents if backend supports or do separately)
@router.delete("/admin/sessions/{session_id}")
async def remove_session(session_id: str):
    try:
        await delete_session(session_id)
        return {"message": f"Session {session_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete a message by ID
@router.delete("/admin/messages/{message_id}")
async def remove_message(message_id: str):
    try:
        await delete_message(message_id)
        return {"message": f"Message {message_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete a document by ID
@router.delete("/admin/documents/{document_id}")
async def remove_document(document_id: str):
    try:
        await delete_document(document_id)
        return {"message": f"Document {document_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
