#backend/db/models/intervention_model.py
"""
Modelo de Intervenciones
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, CheckConstraint, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.db.base_class import Base

class Intervention(Base):
    __tablename__ = "interventions"
    
    intervention_id = Column(Integer, primary_key=True, index=True)
    technician_id = Column(Integer, ForeignKey("technicians.technician_id"))
    client_id = Column(Integer, ForeignKey("clients.client_id"))
    equipment_id = Column(Integer, ForeignKey("installed_equipment.equipment_id"))
    scheduled_date = Column(Date, nullable=False)
    type = Column(String, CheckConstraint("type IN ('instalacion', 'mantenimiento', 'reparacion', 'retirada')"))
    description = Column(Text)
    result = Column(Text)
    document_url = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    technician = relationship("Technician", back_populates="interventions")
    client = relationship("Client", back_populates="interventions")
    equipment = relationship("InstalledEquipment", back_populates="interventions")
