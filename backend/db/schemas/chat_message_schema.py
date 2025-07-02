#backend/db/schemas/chat_message_schema.py
"""
Esquemas Pydantic para Mensaje de Chat
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Esquema base
class ChatMessageBase(BaseModel):
    chat_id: str
    message_timestamp: datetime
    sender: str  # cliente, agente, sistema
    message_text: str

# Esquema para crear mensaje de chat
class ChatMessageCreate(ChatMessageBase):
    pass

# Esquema para actualizar mensaje de chat
class ChatMessageUpdate(BaseModel):
    chat_id: Optional[str] = None
    message_timestamp: Optional[datetime] = None
    sender: Optional[str] = None
    message_text: Optional[str] = None

# Esquema de respuesta
class ChatMessageResponse(ChatMessageBase):
    message_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Esquema de respuesta con relaciones
class ChatMessageWithRelations(ChatMessageResponse):
    # Estas relaciones se pueden agregar cuando se necesiten
    # chat_session: Optional["ChatSessionResponse"] = None
    pass 