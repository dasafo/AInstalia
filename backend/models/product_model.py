#backend/db/models/product_model.py
"""
Modelo de Producto
"""
from sqlalchemy import Column, String, Text, Numeric, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base_class import Base

class Product(Base):
    __tablename__ = "products"
    
    sku = Column(String, primary_key=True, index=True)  # SKU como primary key según el SQL
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2))
    spec_json = Column(JSON)  # JSONB según el SQL original
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    order_items = relationship("OrderItem", back_populates="product")
    installed_equipment = relationship("InstalledEquipment", back_populates="product")
    stock_items = relationship("Stock", back_populates="product")
