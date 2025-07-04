#backend/db/crud/chat_message_crud.py
"""
Operaciones CRUD para Mensaje de Chat
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.chat_message_model import ChatMessage
from backend.schemas.chat_message_schema import ChatMessageCreate, ChatMessageUpdate
from backend.crud.base_crud import CRUDBase


class CRUDChatMessage(CRUDBase[ChatMessage, ChatMessageCreate, ChatMessageUpdate]):
    def __init__(self):
        super().__init__(ChatMessage)

    async def get(self, db: AsyncSession, message_id: int) -> Optional[ChatMessage]:
        """Obtener mensaje por ID"""
        return await super().get(db, id=message_id)

    async def get_by_chat(self, db: AsyncSession, *, chat_id: str) -> List[ChatMessage]:
        """Obtener todos los mensajes de una sesión de chat"""
        result = await db.execute(select(ChatMessage).filter(ChatMessage.chat_id == chat_id).order_by(ChatMessage.message_timestamp))
        return result.scalars().all()

    async def get_by_sender(self, db: AsyncSession, *, sender: str) -> List[ChatMessage]:
        """Obtener mensajes por tipo de remitente (cliente, agente, sistema)"""
        result = await db.execute(select(ChatMessage).filter(ChatMessage.sender == sender))
        return result.scalars().all()

    async def get_by_chat_and_sender(self, db: AsyncSession, *, chat_id: str, sender: str) -> List[ChatMessage]:
        """Obtener mensajes de un chat específico y remitente"""
        result = await db.execute(select(ChatMessage).filter(
            ChatMessage.chat_id == chat_id,
            ChatMessage.sender == sender
        ).order_by(ChatMessage.message_timestamp))
        return result.scalars().all()

    async def get_by_date_range(
        self, db: AsyncSession, *, start_date: datetime, end_date: datetime
    ) -> List[ChatMessage]:
        """Obtener mensajes en rango de fechas"""
        result = await db.execute(select(ChatMessage).filter(
            ChatMessage.message_timestamp >= start_date,
            ChatMessage.message_timestamp <= end_date
        ))
        return result.scalars().all()

    async def search_by_text(self, db: AsyncSession, *, text: str) -> List[ChatMessage]:
        """Buscar mensajes por contenido de texto (búsqueda parcial)"""
        result = await db.execute(select(ChatMessage).filter(ChatMessage.message_text.ilike(f"%{text}%")))
        return result.scalars().all()

    async def get_latest_messages_by_chat(self, db: AsyncSession, *, chat_id: str, limit: int = 10) -> List[ChatMessage]:
        """Obtener los últimos N mensajes de una sesión de chat"""
        result = await db.execute(select(ChatMessage).filter(ChatMessage.chat_id == chat_id).order_by(
            ChatMessage.message_timestamp.desc()
        ).limit(limit))
        return result.scalars().all()

    async def get_client_messages(self, db: AsyncSession, *, chat_id: str) -> List[ChatMessage]:
        """Obtener solo mensajes del cliente en una sesión"""
        return await self.get_by_chat_and_sender(db, chat_id=chat_id, sender="cliente")

    async def get_agent_messages(self, db: AsyncSession, *, chat_id: str) -> List[ChatMessage]:
        """Obtener solo mensajes del agente en una sesión"""
        return await self.get_by_chat_and_sender(db, chat_id=chat_id, sender="agente")

    async def remove(self, db: AsyncSession, *, message_id: int) -> Optional[ChatMessage]:
        """Eliminar mensaje por ID"""
        return await super().remove(db, id=message_id)

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[ChatMessage]:
        """Obtener múltiples mensajes de chat con paginación"""
        result = await db.execute(select(ChatMessage).offset(skip).limit(limit))
        return result.scalars().all() 