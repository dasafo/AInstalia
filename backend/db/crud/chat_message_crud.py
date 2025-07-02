#backend/db/crud/chat_message_crud.py
"""
Operaciones CRUD para Mensaje de Chat
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.db.models.chat_message_model import ChatMessage
from backend.db.schemas.chat_message_schema import ChatMessageCreate, ChatMessageUpdate
from backend.db.crud.base_crud import CRUDBase


class CRUDChatMessage(CRUDBase[ChatMessage, ChatMessageCreate, ChatMessageUpdate]):
    def __init__(self):
        super().__init__(ChatMessage)

    def get(self, db: Session, message_id: int) -> Optional[ChatMessage]:
        """Obtener mensaje por ID"""
        return db.query(ChatMessage).filter(ChatMessage.message_id == message_id).first()

    def get_by_chat(self, db: Session, *, chat_id: str) -> List[ChatMessage]:
        """Obtener todos los mensajes de una sesión de chat"""
        return db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).order_by(ChatMessage.message_timestamp).all()

    def get_by_sender(self, db: Session, *, sender: str) -> List[ChatMessage]:
        """Obtener mensajes por tipo de remitente (cliente, agente, sistema)"""
        return db.query(ChatMessage).filter(ChatMessage.sender == sender).all()

    def get_by_chat_and_sender(self, db: Session, *, chat_id: str, sender: str) -> List[ChatMessage]:
        """Obtener mensajes de un chat específico y remitente"""
        return db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat_id,
            ChatMessage.sender == sender
        ).order_by(ChatMessage.message_timestamp).all()

    def get_by_date_range(
        self, db: Session, *, start_date: datetime, end_date: datetime
    ) -> List[ChatMessage]:
        """Obtener mensajes en rango de fechas"""
        return db.query(ChatMessage).filter(
            ChatMessage.message_timestamp >= start_date,
            ChatMessage.message_timestamp <= end_date
        ).all()

    def search_by_text(self, db: Session, *, text: str) -> List[ChatMessage]:
        """Buscar mensajes por contenido de texto (búsqueda parcial)"""
        return db.query(ChatMessage).filter(ChatMessage.message_text.ilike(f"%{text}%")).all()

    def get_latest_messages_by_chat(self, db: Session, *, chat_id: str, limit: int = 10) -> List[ChatMessage]:
        """Obtener los últimos N mensajes de una sesión de chat"""
        return db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).order_by(
            ChatMessage.message_timestamp.desc()
        ).limit(limit).all()

    def get_client_messages(self, db: Session, *, chat_id: str) -> List[ChatMessage]:
        """Obtener solo mensajes del cliente en una sesión"""
        return self.get_by_chat_and_sender(db, chat_id=chat_id, sender="cliente")

    def get_agent_messages(self, db: Session, *, chat_id: str) -> List[ChatMessage]:
        """Obtener solo mensajes del agente en una sesión"""
        return self.get_by_chat_and_sender(db, chat_id=chat_id, sender="agente")

    def remove(self, db: Session, *, message_id: int) -> ChatMessage:
        """Eliminar mensaje por ID"""
        obj = db.query(ChatMessage).filter(ChatMessage.message_id == message_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj 