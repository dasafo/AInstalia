#backend/db/schemas/chat_session_schema.py
"""
Esquemas Pydantic para Sesión de Chat
"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict

# Esquema base
class ChatSessionBase(BaseModel):
    chat_id: str
    order_id: Optional[str] = None
    client_id: int
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None
    topic: Optional[str] = None

# Esquema para crear sesión de chat
class ChatSessionCreate(BaseModel):
    chat_id: str
    order_id: Optional[str] = None
    client_id: int
    topic: Optional[str] = None

# Esquema para actualizar sesión de chat
class ChatSessionUpdate(BaseModel):
    order_id: Optional[str] = None
    client_id: Optional[int] = None
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None
    topic: Optional[str] = None

# Esquema de respuesta
class ChatSessionResponse(ChatSessionBase):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Esquema con relaciones
class ChatSessionWithRelations(ChatSessionResponse):
    client: Optional[Dict] = None
    messages: Optional[List[Dict]] = None 