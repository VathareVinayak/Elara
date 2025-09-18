from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Session(BaseModel):
    id: str
    created_at: Optional[datetime]
    status: Optional[str] = "active"
    user_id: Optional[str] = None
    
class Message(BaseModel):
    id: str
    session_id: str
    content: str
    created_at: Optional[datetime]
    role: Optional[str] = "user"
    message_type: Optional[str] = "text"
    
class Document(BaseModel):
    id: str
    file_name: str
    session_id: str
    upload_time: Optional[datetime]
    file_url: Optional[str] = None
    do_not_store: Optional[bool] = False
