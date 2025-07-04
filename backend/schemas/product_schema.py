#backend/db/schemas/product_schema.py
"""
Esquemas Pydantic para Producto
"""
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, field_serializer

# Esquema base
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[Decimal] = None
    spec_json: Optional[Dict[str, Any]] = None

    @field_serializer('price')
    def serialize_price(self, price: Optional[Decimal]) -> Optional[float]:
        if price is None:
            return None
        return float(price)

# Esquema para crear producto
class ProductCreate(ProductBase):
    sku: str

# Esquema para actualizar producto
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    spec_json: Optional[Dict[str, Any]] = None

# Esquema de respuesta
class ProductResponse(ProductBase):
    sku: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# Esquema de respuesta con relaciones
class ProductWithRelations(ProductResponse):
    # Estas relaciones se pueden agregar cuando se necesiten
    # order_items: List["OrderItemResponse"] = []
    # stock_items: List["StockResponse"] = []
    pass 