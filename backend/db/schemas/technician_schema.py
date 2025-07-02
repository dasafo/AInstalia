#backend/db/schemas/technician_schema.py
"""
Esquemas Pydantic para Técnico
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Esquema base
class TechnicianBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    specialization: Optional[str] = None

# Esquema para crear técnico
class TechnicianCreate(TechnicianBase):
    pass

# Esquema para actualizar técnico
class TechnicianUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None

# Esquema de respuesta
class TechnicianResponse(TechnicianBase):
    technician_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Esquema de respuesta con relaciones
class TechnicianWithRelations(TechnicianResponse):
    # Estas relaciones se pueden agregar cuando se necesiten
    # interventions: List["InterventionResponse"] = []
    pass 