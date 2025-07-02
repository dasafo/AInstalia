#backend/db/schemas/contract_schema.py
"""
Esquemas Pydantic para Contrato
"""
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel

# Esquema base
class ContractBase(BaseModel):
    client_id: int
    contract_type: str
    start_date: date
    end_date: Optional[date] = None
    monthly_cost: Optional[Decimal] = None
    status: str

# Esquema para crear contrato
class ContractCreate(ContractBase):
    pass

# Esquema para actualizar contrato
class ContractUpdate(BaseModel):
    client_id: Optional[int] = None
    contract_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    monthly_cost: Optional[Decimal] = None
    status: Optional[str] = None

# Esquema de respuesta
class ContractResponse(ContractBase):
    contract_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Esquema de respuesta con relaciones
class ContractWithRelations(ContractResponse):
    # Estas relaciones se pueden agregar cuando se necesiten
    # client: Optional["ClientResponse"] = None
    pass 