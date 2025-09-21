#backend/db/models/contract_model.py
"""
Modelo de Contratos
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.db.base_class import Base

class Contract(Base):
    __tablename__ = "contracts"
    
    contract_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    type = Column(String)
    terms = Column(Text)
    
    # Relaciones
    client = relationship("Client", back_populates="contracts")
