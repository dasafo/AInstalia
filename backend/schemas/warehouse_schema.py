#backend/db/schemas/warehouse_schema.py
"""
Esquemas Pydantic para Almacén
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

# Esquema base
class WarehouseBase(BaseModel):
    name: str

# Esquema para crear almacén
class WarehouseCreate(WarehouseBase):
    pass

# Esquema para actualizar almacén
class WarehouseUpdate(BaseModel):
    name: Optional[str] = None

# Esquema de respuesta
class WarehouseResponse(WarehouseBase):
    warehouse_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Esquema de respuesta con relaciones
class WarehouseWithRelations(WarehouseResponse):
    # Estas relaciones se pueden agregar cuando se necesiten
    # stock_items: List["StockResponse"] = []
    pass 