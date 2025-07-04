#backend/db/crud/knowledge_feedback_crud.py
"""
Operaciones CRUD para Feedback de Conocimiento
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.knowledge_feedback_model import KnowledgeFeedback
from backend.schemas.knowledge_feedback_schema import KnowledgeFeedbackCreate, KnowledgeFeedbackUpdate
from backend.crud.base_crud import CRUDBase


class CRUDKnowledgeFeedback(CRUDBase[KnowledgeFeedback, KnowledgeFeedbackCreate, KnowledgeFeedbackUpdate]):
    def __init__(self):
        super().__init__(KnowledgeFeedback)

    async def get(self, db: AsyncSession, feedback_id: int) -> Optional[KnowledgeFeedback]:
        """Obtener feedback por ID"""
        return await super().get(db, id=feedback_id)

    async def get_by_status(self, db: AsyncSession, *, status: str, skip: int = 0, limit: int = 100) -> List[KnowledgeFeedback]:
        """Obtener feedback por estado con paginación"""
        result = await db.execute(select(KnowledgeFeedback).filter(KnowledgeFeedback.status == status).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_user_type(self, db: AsyncSession, *, user_type: str, skip: int = 0, limit: int = 100) -> List[KnowledgeFeedback]:
        """Obtener feedback por tipo de usuario con paginación"""
        result = await db.execute(select(KnowledgeFeedback).filter(KnowledgeFeedback.user_type == user_type).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_user_type_and_status(self, db: AsyncSession, *, user_type: str, status: str, skip: int = 0, limit: int = 100) -> List[KnowledgeFeedback]:
        """Obtener feedback por tipo de usuario y estado con paginación"""
        result = await db.execute(select(KnowledgeFeedback).filter(
            KnowledgeFeedback.user_type == user_type,
            KnowledgeFeedback.status == status
        ).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_pending_feedback(self, db: AsyncSession) -> List[KnowledgeFeedback]:
        """Obtener feedback pendiente de revisión"""
        result = await db.execute(select(KnowledgeFeedback).filter(KnowledgeFeedback.status == "pendiente"))
        return result.scalars().all()

    async def get_approved_feedback(self, db: AsyncSession) -> List[KnowledgeFeedback]:
        """Obtener feedback aprobado"""
        result = await db.execute(select(KnowledgeFeedback).filter(KnowledgeFeedback.status == "aprobado"))
        return result.scalars().all()

    async def search_by_question(self, db: AsyncSession, *, question: str) -> List[KnowledgeFeedback]:
        """Buscar feedback por pregunta (búsqueda parcial)"""
        result = await db.execute(select(KnowledgeFeedback).filter(KnowledgeFeedback.question.ilike(f"%{question}%")))
        return result.scalars().all()

    async def search_by_answer(self, db: AsyncSession, *, answer: str) -> List[KnowledgeFeedback]:
        """Buscar feedback por respuesta esperada (búsqueda parcial)"""
        result = await db.execute(select(KnowledgeFeedback).filter(KnowledgeFeedback.expected_answer.ilike(f"%{answer}%")))
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, feedback_id: int) -> Optional[KnowledgeFeedback]:
        """Eliminar feedback por ID"""
        return await super().remove(db, id=feedback_id)

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[KnowledgeFeedback]:
        """Obtener múltiples feedbacks con paginación"""
        result = await db.execute(select(KnowledgeFeedback).offset(skip).limit(limit))
        return result.scalars().all()