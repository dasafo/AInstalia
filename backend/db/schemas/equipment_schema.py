#backend/db/schemas/equipment_schema.py
"""
Esquemas Pydantic para Equipo Instalado
"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel

# Esquema base
class InstalledEquipmentBase(BaseModel):
    sku: str
    installation_date: date
    status: str
    client_id: int

# Esquema para crear equipo instalado
class InstalledEquipmentCreate(InstalledEquipmentBase):
    pass

# Esquema para actualizar equipo instalado
class InstalledEquipmentUpdate(BaseModel):
    sku: Optional[str] = None
    installation_date: Optional[date] = None
    status: Optional[str] = None
    client_id: Optional[int] = None

# Esquema de respuesta
class InstalledEquipmentResponse(InstalledEquipmentBase):
    equipment_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Esquema de respuesta con relaciones
class InstalledEquipmentWithRelations(InstalledEquipmentResponse):
    # Estas relaciones se pueden agregar cuando se necesiten
    # product: Optional["ProductResponse"] = None
    # client: Optional["ClientResponse"] = None
    # interventions: List["InterventionResponse"] = []
    pass 