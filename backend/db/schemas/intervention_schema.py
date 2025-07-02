#backend/db/schemas/intervention_schema.py
"""
Esquemas Pydantic para Intervención
"""
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel

# Esquema base
class InterventionBase(BaseModel):
    equipment_id: int
    technician_id: int
    client_id: int
    intervention_date: date
    description: Optional[str] = None
    hours_worked: Optional[Decimal] = None
    status: str

# Esquema para crear intervención
class InterventionCreate(InterventionBase):
    pass

# Esquema para actualizar intervención
class InterventionUpdate(BaseModel):
    equipment_id: Optional[int] = None
    technician_id: Optional[int] = None
    client_id: Optional[int] = None
    intervention_date: Optional[date] = None
    description: Optional[str] = None
    hours_worked: Optional[Decimal] = None
    status: Optional[str] = None

# Esquema de respuesta
class InterventionResponse(InterventionBase):
    intervention_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Esquema de respuesta con relaciones
class InterventionWithRelations(InterventionResponse):
    # Estas relaciones se pueden agregar cuando se necesiten
    # equipment: Optional["InstalledEquipmentResponse"] = None
    # technician: Optional["TechnicianResponse"] = None
    # client: Optional["ClientResponse"] = None
    pass 