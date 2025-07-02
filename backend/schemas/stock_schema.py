#backend/db/schemas/stock_schema.py
"""
Esquemas Pydantic para Stock/Inventario
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

# Esquema base
class StockBase(BaseModel):
    sku: str
    warehouse_id: int
    quantity: int = 0

# Esquema para crear stock
class StockCreate(StockBase):
    pass

# Esquema para actualizar stock
class StockUpdate(BaseModel):
    sku: Optional[str] = None
    warehouse_id: Optional[int] = None
    quantity: Optional[int] = None

# Esquema de respuesta
class StockResponse(StockBase):
    stock_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Esquema de respuesta con relaciones
class StockWithRelations(StockResponse):
    # Estas relaciones se pueden agregar cuando se necesiten
    # product: Optional["ProductResponse"] = None
    # warehouse: Optional["WarehouseResponse"] = None
    pass 