#backend/db/models/stock_model.py
"""
Modelo de Stock/Inventario
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base_class import Base

class Stock(Base):
    __tablename__ = "stock"
    
    stock_id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, ForeignKey("products.sku"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    product = relationship("Product", back_populates="stock_items")
    warehouse = relationship("Warehouse", back_populates="stock_items") 
