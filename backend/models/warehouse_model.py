#backend/db/models/warehouse_model.py
"""
Modelo de Almacén
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base_class import Base

class Warehouse(Base):
    __tablename__ = "warehouses"
    
    warehouse_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    stock_items = relationship("Stock", back_populates="warehouse") 
