#backend/db/schemas/knowledge_feedback_schema.py
"""
Esquemas Pydantic para Feedback de Conocimiento
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Esquema base
class KnowledgeFeedbackBase(BaseModel):
    question: str
    expected_answer: str
    user_type: str  # cliente, tecnico, administrador
    status: str = "pendiente"  # pendiente, revisado, aprobado

# Esquema para crear feedback
class KnowledgeFeedbackCreate(KnowledgeFeedbackBase):
    pass

# Esquema para actualizar feedback
class KnowledgeFeedbackUpdate(BaseModel):
    question: Optional[str] = None
    expected_answer: Optional[str] = None
    user_type: Optional[str] = None
    status: Optional[str] = None

# Esquema de respuesta
class KnowledgeFeedbackResponse(KnowledgeFeedbackBase):
    feedback_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Sin relaciones - tabla independiente para análisis de conocimiento 