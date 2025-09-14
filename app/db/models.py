from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Session(BaseModel):
    id: str
    created_at: Optional[datetime]

class Message(BaseModel):
    id: str
    session_id: str
    content: str
    created_at: Optional[datetime]

class Document(BaseModel):
    id: str
    file_name: str
    session_id: str
    upload_time: Optional[datetime]


    