#backend/db/models/equipment_model.py
"""
Modelo de Equipos Instalados
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.db.base_class import Base

class InstalledEquipment(Base):
    __tablename__ = "installed_equipment"
    
    equipment_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"))
    sku = Column(String, ForeignKey("products.sku"))
    install_date = Column(Date)
    status = Column(String, default="activo")
    config_json = Column(JSON)
    
    # Relaciones
    product = relationship("Product", back_populates="installed_equipment")
    client = relationship("Client", back_populates="installed_equipment")
    interventions = relationship("Intervention", back_populates="equipment")
