#backend/db/models/chat_session_model.py
"""
Modelo de Sesión de Chat
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base_class import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    chat_id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    start_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    end_timestamp = Column(DateTime(timezone=True), nullable=True)
    topic = Column(String, nullable=True)
    
    # Timestamps adicionales
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    order = relationship("Order", back_populates="chat_sessions")
    client = relationship("Client", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="chat_session") 
