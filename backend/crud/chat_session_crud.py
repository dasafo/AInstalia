#backend/db/crud/chat_session_crud.py
"""
Operaciones CRUD para Sesión de Chat
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.models.chat_session_model import ChatSession
from backend.schemas.chat_session_schema import ChatSessionCreate, ChatSessionUpdate
from backend.crud.base_crud import CRUDBase


class CRUDChatSession(CRUDBase[ChatSession, ChatSessionCreate, ChatSessionUpdate]):
    def __init__(self):
        super().__init__(ChatSession)

    def get(self, db: Session, chat_id: str) -> Optional[ChatSession]:
        """Obtener sesión de chat por ID"""
        return db.query(ChatSession).filter(ChatSession.chat_id == chat_id).first()

    def get_by_client(self, db: Session, *, client_id: int) -> List[ChatSession]:
        """Obtener sesiones de chat de un cliente"""
        return db.query(ChatSession).filter(ChatSession.client_id == client_id).all()

    def get_by_order(self, db: Session, *, order_id: str) -> List[ChatSession]:
        """Obtener sesiones de chat asociadas a un pedido"""
        return db.query(ChatSession).filter(ChatSession.order_id == order_id).all()

    def get_by_topic(self, db: Session, *, topic: str) -> List[ChatSession]:
        """Obtener sesiones de chat por tema"""
        return db.query(ChatSession).filter(ChatSession.topic == topic).all()

    def get_active_sessions(self, db: Session) -> List[ChatSession]:
        """Obtener sesiones de chat activas (sin fecha de fin)"""
        return db.query(ChatSession).filter(ChatSession.end_timestamp.is_(None)).all()

    def get_completed_sessions(self, db: Session) -> List[ChatSession]:
        """Obtener sesiones de chat completadas (con fecha de fin)"""
        return db.query(ChatSession).filter(ChatSession.end_timestamp.isnot(None)).all()

    def get_by_date_range(
        self, db: Session, *, start_date: datetime, end_date: datetime
    ) -> List[ChatSession]:
        """Obtener sesiones de chat en rango de fechas"""
        return db.query(ChatSession).filter(
            ChatSession.start_timestamp >= start_date,
            ChatSession.start_timestamp <= end_date
        ).all()

    def search_by_topic(self, db: Session, *, topic: str) -> List[ChatSession]:
        """Buscar sesiones por tema (búsqueda parcial)"""
        return db.query(ChatSession).filter(ChatSession.topic.ilike(f"%{topic}%")).all()

    def remove(self, db: Session, *, chat_id: str) -> ChatSession:
        """Eliminar sesión de chat por ID"""
        obj = db.query(ChatSession).filter(ChatSession.chat_id == chat_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ChatSession]:
        """Obtener múltiples sesiones de chat con paginación"""
        return db.query(ChatSession).offset(skip).limit(limit).all() 