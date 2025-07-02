#backend/db/schemas/technician_schema.py
"""
Esquemas Pydantic para Técnico
"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict

# Esquema base
class TechnicianBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    zone: Optional[str] = None  # Coincidir con SQL: zone

# Esquema para crear técnico
class TechnicianCreate(TechnicianBase):
    pass

# Esquema para actualizar técnico
class TechnicianUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    zone: Optional[str] = None

# Esquema de respuesta
class TechnicianResponse(TechnicianBase):
    technician_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Esquema con relaciones
class TechnicianWithRelations(TechnicianResponse):
    interventions: Optional[List[Dict]] = None
    # Estas relaciones se pueden agregar cuando se necesiten
    # interventions: List["InterventionResponse"] = []
    pass 