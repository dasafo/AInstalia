#backend/db/schemas/chat_session_schema.py
"""
Esquemas Pydantic para Sesión de Chat
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# Esquema base
class ChatSessionBase(BaseModel):
    order_id: Optional[str] = None
    client_id: int
    end_timestamp: Optional[datetime] = None
    topic: Optional[str] = None

# Esquema para crear sesión de chat
class ChatSessionCreate(ChatSessionBase):
    chat_id: str

# Esquema para actualizar sesión de chat
class ChatSessionUpdate(BaseModel):
    order_id: Optional[str] = None
    client_id: Optional[int] = None
    end_timestamp: Optional[datetime] = None
    topic: Optional[str] = None

# Esquema de respuesta
class ChatSessionResponse(ChatSessionBase):
    chat_id: str
    start_timestamp: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Esquema de respuesta con relaciones
class ChatSessionWithRelations(ChatSessionResponse):
    # Estas relaciones se pueden agregar cuando se necesiten
    # order: Optional["OrderResponse"] = None
    # client: Optional["ClientResponse"] = None
    # messages: List["ChatMessageResponse"] = []
    pass 