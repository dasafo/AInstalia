#backend/db/models/client_model.py
"""
Modelo de Cliente
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from backend.db.base_class import Base

class Client(Base):
    __tablename__ = "clients"
    
    client_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(Text)
    
    # Relaciones
    contracts = relationship("Contract", back_populates="client")
    interventions = relationship("Intervention", back_populates="client")
    installed_equipment = relationship("InstalledEquipment", back_populates="client")
    orders = relationship("Order", back_populates="client")
    chat_sessions = relationship("ChatSession", back_populates="client")
