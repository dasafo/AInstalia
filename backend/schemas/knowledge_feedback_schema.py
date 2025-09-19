#backend/db/schemas/knowledge_feedback_schema.py
"""
Esquemas Pydantic para Feedback de Conocimiento
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, ConfigDict, Field
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
    user_comment: Optional[str] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    user_type: UserType
    status: FeedbackStatus = FeedbackStatus.PENDIENTE

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, value):
        if value is None:
            return value
        if not 1 <= value <= 5:
            raise ValueError("rating debe estar entre 1 y 5")
        return value

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
