#backend/db/schemas/order_schema.py
"""
Esquemas Pydantic para Pedido y Elementos de Pedido
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel

# === ESQUEMAS PARA ORDER ===

# Esquema base para pedido
class OrderBase(BaseModel):
    client_id: int
    chat_id: Optional[str] = None
    total_amount: Optional[Decimal] = None
    status: str = "pendiente"

# Esquema para crear pedido
class OrderCreate(OrderBase):
    order_id: str

# Esquema para actualizar pedido
class OrderUpdate(BaseModel):
    client_id: Optional[int] = None
    chat_id: Optional[str] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None

# Esquema de respuesta para pedido
class OrderResponse(OrderBase):
    order_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# === ESQUEMAS PARA ORDER ITEM ===

# Esquema base para elemento de pedido
class OrderItemBase(BaseModel):
    order_id: str
    product_sku: str
    quantity: int
    price: Optional[Decimal] = None

# Esquema para crear elemento de pedido
class OrderItemCreate(OrderItemBase):
    pass

# Esquema para actualizar elemento de pedido
class OrderItemUpdate(BaseModel):
    order_id: Optional[str] = None
    product_sku: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[Decimal] = None

# Esquema de respuesta para elemento de pedido
class OrderItemResponse(OrderItemBase):
    item_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# === ESQUEMAS CON RELACIONES ===

# Esquema de respuesta con relaciones para pedido
class OrderWithRelations(OrderResponse):
    items: List[OrderItemResponse] = []
    # client: Optional["ClientResponse"] = None

# Esquema de respuesta con relaciones para elemento de pedido
class OrderItemWithRelations(OrderItemResponse):
    # order: Optional["OrderResponse"] = None
    # product: Optional["ProductResponse"] = None
    pass 