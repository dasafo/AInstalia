#backend/db/schemas/intervention_schema.py
"""
Esquemas Pydantic para Intervención
"""
from datetime import datetime, date
from typing import Optional, Dict
from decimal import Decimal
from pydantic import BaseModel, field_validator, ConfigDict

# Esquema base
class InterventionBase(BaseModel):
    technician_id: int
    client_id: int
    equipment_id: Optional[int] = None
    scheduled_date: date  # Cambiado de 'date' a 'scheduled_date' para coincidir con el test
    type: str  # instalacion, mantenimiento, reparacion, retirada
    description: Optional[str] = None
    result: Optional[str] = None
    document_url: Optional[str] = None
    
    @field_validator('scheduled_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Fecha debe estar en formato YYYY-MM-DD')
        return v

# Esquema para crear intervención
class InterventionCreate(InterventionBase):
    pass

# Esquema para actualizar intervención
class InterventionUpdate(BaseModel):
    technician_id: Optional[int] = None
    client_id: Optional[int] = None
    equipment_id: Optional[int] = None
    scheduled_date: Optional[date] = None
    type: Optional[str] = None
    description: Optional[str] = None
    result: Optional[str] = None
    document_url: Optional[str] = None
    
    @field_validator('scheduled_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Fecha debe estar en formato YYYY-MM-DD')
        return v

# Esquema de respuesta
class InterventionResponse(InterventionBase):
    intervention_id: int

    model_config = ConfigDict(from_attributes=True)

# Esquema con relaciones
class InterventionWithRelations(InterventionResponse):
    technician: Optional[Dict] = None
    client: Optional[Dict] = None
    equipment: Optional[Dict] = None 