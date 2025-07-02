#backend/db/crud/knowledge_feedback_crud.py
"""
Operaciones CRUD para Feedback de Conocimiento
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.db.models.knowledge_feedback_model import KnowledgeFeedback
from backend.db.schemas.knowledge_feedback_schema import KnowledgeFeedbackCreate, KnowledgeFeedbackUpdate
from backend.db.crud.base_crud import CRUDBase


class CRUDKnowledgeFeedback(CRUDBase[KnowledgeFeedback, KnowledgeFeedbackCreate, KnowledgeFeedbackUpdate]):
    def __init__(self):
        super().__init__(KnowledgeFeedback)

    def get(self, db: Session, feedback_id: int) -> Optional[KnowledgeFeedback]:
        """Obtener feedback por ID"""
        return db.query(KnowledgeFeedback).filter(KnowledgeFeedback.feedback_id == feedback_id).first()

    def get_by_status(self, db: Session, *, status: str) -> List[KnowledgeFeedback]:
        """Obtener feedback por estado"""
        return db.query(KnowledgeFeedback).filter(KnowledgeFeedback.status == status).all()

    def get_by_user_type(self, db: Session, *, user_type: str) -> List[KnowledgeFeedback]:
        """Obtener feedback por tipo de usuario"""
        return db.query(KnowledgeFeedback).filter(KnowledgeFeedback.user_type == user_type).all()

    def get_pending_feedback(self, db: Session) -> List[KnowledgeFeedback]:
        """Obtener feedback pendiente de revisión"""
        return db.query(KnowledgeFeedback).filter(KnowledgeFeedback.status == "pendiente").all()

    def get_approved_feedback(self, db: Session) -> List[KnowledgeFeedback]:
        """Obtener feedback aprobado"""
        return db.query(KnowledgeFeedback).filter(KnowledgeFeedback.status == "aprobado").all()

    def search_by_question(self, db: Session, *, question: str) -> List[KnowledgeFeedback]:
        """Buscar feedback por pregunta (búsqueda parcial)"""
        return db.query(KnowledgeFeedback).filter(KnowledgeFeedback.question.ilike(f"%{question}%")).all()

    def search_by_answer(self, db: Session, *, answer: str) -> List[KnowledgeFeedback]:
        """Buscar feedback por respuesta esperada (búsqueda parcial)"""
        return db.query(KnowledgeFeedback).filter(KnowledgeFeedback.expected_answer.ilike(f"%{answer}%")).all()

    def remove(self, db: Session, *, feedback_id: int) -> KnowledgeFeedback:
        """Eliminar feedback por ID"""
        obj = db.query(KnowledgeFeedback).filter(KnowledgeFeedback.feedback_id == feedback_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj 