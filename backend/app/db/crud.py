from typing import Optional, List
from datetime import datetime

from backend.app.db.supabase_client import supabase

# 1) Sessions

# Creating Sessions
async def create_session(user_id: Optional[str] = None) -> str:
    data = {"user_id": user_id, "status": "active"}
    response = supabase.table("sessions").insert(data).execute()
    if hasattr(response, "error") and response.error:
        raise Exception(f"Failed to create session: {response.error.message}")
    if not response.data:
        raise Exception("No data returned from Supabase")
    return response.data[0]["id"]

# Fetch Session
async def get_session(session_id: str) -> Optional[dict]:
    response = supabase.table("sessions").select("*").eq("id", session_id).execute()
    if hasattr(response, "error") and response.error:
        return None
    if not response.data:
        return None
    return response.data[0]

# Get All Session
async def get_all_sessions() -> list[dict]:
    response = supabase.table("sessions").select("*").order("created_at", desc=True).execute()
    if hasattr(response, "error") and response.error:
        raise Exception(f"Failed to get sessions: {response.error.message}")
    if not response.data:
        return []
    return response.data


# 2) Messages
# Create Message 
async def create_message(session_id: str, content: str, role: str = "user", message_type: str = "text") -> str:
    data = {
        "session_id": session_id,
        "content": content,
        "role": role,
        "message_type": message_type,
        "created_at": datetime.utcnow().isoformat()
    }
    response = supabase.table("messages").insert(data).execute()
    if hasattr(response, "error") and response.error:
        raise Exception(f"Failed to create message: {response.error.message}")
    if not response.data:
        raise Exception("No data returned from Supabase")
    return response.data[0]["id"]

# Fetch Message By session_id
async def get_messages_by_session(session_id: str) -> List[dict]:
    response = supabase.table("messages").select("*").eq("session_id", session_id).order("created_at").execute()
    if hasattr(response, "error") and response.error:
        raise Exception(f"Failed to get messages: {response.error.message}")
    if not response.data:
        return []
    return response.data


# 3) Documents
# Create Document
async def create_document(session_id: Optional[str], file_name: str, file_url: str, do_not_store: bool = False) -> str:
    data = {
        "session_id": session_id,
        "file_name": file_name,
        "file_url": file_url,
        "do_not_store": do_not_store,
        "created_at": datetime.utcnow().isoformat()
    }
    response = supabase.table("documents").insert(data).execute()
    if hasattr(response, "error") and response.error:
        raise Exception(f"Failed to create document: {response.error.message}")
    if not response.data:
        raise Exception("No data returned from Supabase")
    return response.data[0]["id"]

# Fetch Document By session_id
async def get_documents_by_session(session_id: str) -> List[dict]:
    response = supabase.table("documents").select("*").eq("session_id", session_id).order("created_at").execute()
    if hasattr(response, "error") and response.error:
        raise Exception(f"Failed to get documents: {response.error.message}")
    if not response.data:
        return []
    return response.data
