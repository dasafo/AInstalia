#backend/db/models/knowledge_feedback_model.py
"""
Modelo de Feedback de Conocimiento
Tabla independiente para mejorar el sistema de IA/RAG
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, SmallInteger
from sqlalchemy.sql import func
from backend.db.base_class import Base

class KnowledgeFeedback(Base):
    __tablename__ = "knowledge_feedback"
    
    feedback_id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    expected_answer = Column(Text, nullable=False)
    user_comment = Column(Text, nullable=True)
    rating = Column(SmallInteger, nullable=True)
    user_type = Column(String, nullable=False)  # cliente, tecnico, administrador
    status = Column(String, nullable=False, default='pendiente')  # pendiente, revisado, aprobado
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Sin relaciones - tabla independiente para análisis de conocimiento 
