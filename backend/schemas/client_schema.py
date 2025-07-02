#backend/db/schemas/client_schema.py
"""
Esquemas Pydantic para Cliente
"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict, field_validator
import re

# Esquema base
class ClientBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validación básica de email"""
        if not v:
            raise ValueError('Email es requerido')
        # Patrón básico de email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Formato de email inválido')
        return v

# Esquema para crear cliente
class ClientCreate(ClientBase):
    pass

# Esquema para actualizar cliente
class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email_update(cls, v):
        """Validación básica de email para actualizaciones"""
        if v is None:
            return v
        # Patrón básico de email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Formato de email inválido')
        return v

# Esquema de respuesta
class ClientResponse(ClientBase):
    client_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Esquema con relaciones
class ClientWithRelations(ClientResponse):
    contracts: Optional[List[Dict]] = None
    interventions: Optional[List[Dict]] = None
    chat_sessions: Optional[List[Dict]] = None
    equipment: Optional[List[Dict]] = None

# Para compatibilidad
ClientInDB = ClientResponse 