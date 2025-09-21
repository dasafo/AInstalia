#backend/db/models/chat_message_model.py
"""
Modelo de Mensaje de Chat
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base_class import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    message_id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, ForeignKey("chat_sessions.chat_id"), nullable=False)
    message_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sender = Column(String, nullable=False)  # cliente, agente, sistema
    message_text = Column(Text, nullable=False)
    
    # Timestamps adicionales
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    chat_session = relationship("ChatSession", back_populates="messages")
