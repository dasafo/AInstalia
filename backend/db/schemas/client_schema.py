#backend/db/schemas/client_schema.py
"""
Esquemas Pydantic para Cliente
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# Esquema base
class ClientBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    company_name: Optional[str] = None
    contact_person: Optional[str] = None

# Esquema para crear cliente
class ClientCreate(ClientBase):
    pass

# Esquema para actualizar cliente
class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    company_name: Optional[str] = None
    contact_person: Optional[str] = None

# Esquema de respuesta
class ClientResponse(ClientBase):
    client_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Esquema de respuesta con relaciones
class ClientWithRelations(ClientResponse):
    # Estas relaciones se pueden agregar cuando se necesiten
    # orders: List["OrderResponse"] = []
    # interventions: List["InterventionResponse"] = []
    pass 