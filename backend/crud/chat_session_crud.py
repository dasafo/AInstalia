#backend/db/crud/chat_session_crud.py
"""
Operaciones CRUD para Sesión de Chat
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.chat_session_model import ChatSession
from backend.schemas.chat_session_schema import ChatSessionCreate, ChatSessionUpdate
from backend.crud.base_crud import CRUDBase


class CRUDChatSession(CRUDBase[ChatSession, ChatSessionCreate, ChatSessionUpdate]):
    def __init__(self):
        super().__init__(ChatSession)

    async def get(self, db: AsyncSession, chat_id: str) -> Optional[ChatSession]:
        """Obtener sesión de chat por ID"""
        return await super().get(db, id=chat_id)

    async def get_by_client(self, db: AsyncSession, *, client_id: int) -> List[ChatSession]:
        """Obtener sesiones de chat de un cliente"""
        result = await db.execute(select(ChatSession).filter(ChatSession.client_id == client_id))
        return result.scalars().all()

    async def get_by_order(self, db: AsyncSession, *, order_id: str) -> List[ChatSession]:
        """Obtener sesiones de chat asociadas a un pedido"""
        result = await db.execute(select(ChatSession).filter(ChatSession.order_id == order_id))
        return result.scalars().all()

    async def get_by_topic(self, db: AsyncSession, *, topic: str) -> List[ChatSession]:
        """Obtener sesiones de chat por tema"""
        result = await db.execute(select(ChatSession).filter(ChatSession.topic == topic))
        return result.scalars().all()

    async def get_active_sessions(self, db: AsyncSession) -> List[ChatSession]:
        """Obtener sesiones de chat activas (sin fecha de fin)"""
        result = await db.execute(select(ChatSession).filter(ChatSession.end_timestamp.is_(None)))
        return result.scalars().all()

    async def get_completed_sessions(self, db: AsyncSession) -> List[ChatSession]:
        """Obtener sesiones de chat completadas (con fecha de fin)"""
        result = await db.execute(select(ChatSession).filter(ChatSession.end_timestamp.isnot(None)))
        return result.scalars().all()

    async def get_by_date_range(
        self, db: AsyncSession, *, start_date: datetime, end_date: datetime
    ) -> List[ChatSession]:
        """Obtener sesiones de chat en rango de fechas"""
        result = await db.execute(select(ChatSession).filter(
            ChatSession.start_timestamp >= start_date,
            ChatSession.start_timestamp <= end_date
        ))
        return result.scalars().all()

    async def search_by_topic(self, db: AsyncSession, *, topic: str) -> List[ChatSession]:
        """Buscar sesiones por tema (búsqueda parcial)"""
        result = await db.execute(select(ChatSession).filter(ChatSession.topic.ilike(f"%{topic}%")))
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, chat_id: str) -> Optional[ChatSession]:
        """Eliminar sesión de chat por ID"""
        return await super().remove(db, id=chat_id)

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[ChatSession]:
        """Obtener múltiples sesiones de chat con paginación"""
        result = await db.execute(select(ChatSession).offset(skip).limit(limit))
        return result.scalars().all() 