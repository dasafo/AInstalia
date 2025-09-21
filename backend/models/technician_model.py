#backend/db/models/technician_model.py
"""
Modelo de Técnico
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base_class import Base

class Technician(Base):
    __tablename__ = "technicians"
    
    technician_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    zone = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    interventions = relationship("Intervention", back_populates="technician")
