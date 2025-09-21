#backend/db/models/order_model.py
"""
Modelo de Pedidos y Items de Pedido
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.base_class import Base

class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(String, primary_key=True, index=True)  # VARCHAR primary key según SQL
    client_id = Column(Integer, ForeignKey("clients.client_id"))
    chat_id = Column(String, nullable=True)
    total_amount = Column(Numeric(10, 2))
    status = Column(String, default="pendiente")
    
    # Relaciones
    client = relationship("Client", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    chat_sessions = relationship("ChatSession", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    item_id = Column(Integer, primary_key=True, index=True)  # Usar item_id según SQL
    order_id = Column(String, ForeignKey("orders.order_id"))  # String FK
    product_sku = Column(String, ForeignKey("products.sku"))  # SKU FK según SQL
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2))  # Usar 'price' según SQL
    
    # Relaciones
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
