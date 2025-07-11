#backend/db/schemas/knowledge_feedback_schema.py
"""
Esquemas Pydantic para Feedback de Conocimiento
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, ConfigDict
from enum import Enum

class UserType(str, Enum):
    CLIENTE = "cliente"
    TECNICO = "tecnico"
    ADMINISTRADOR = "administrador"

class FeedbackStatus(str, Enum):
    PENDIENTE = "pendiente"
    REVISADO = "revisado"
    APROBADO = "aprobado"

# Esquema base
class KnowledgeFeedbackBase(BaseModel):
    question: str
    expected_answer: str
    user_type: UserType
    status: FeedbackStatus = FeedbackStatus.PENDIENTE

# Esquema para crear feedback
class KnowledgeFeedbackCreate(KnowledgeFeedbackBase):
    pass

# Esquema para actualizar feedback
class KnowledgeFeedbackUpdate(BaseModel):
    question: Optional[str] = None
    expected_answer: Optional[str] = None
    user_type: Optional[UserType] = None
    status: Optional[FeedbackStatus] = None

# Esquema de respuesta
class KnowledgeFeedbackResponse(KnowledgeFeedbackBase):
    feedback_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Sin relaciones - tabla independiente para análisis de conocimiento 