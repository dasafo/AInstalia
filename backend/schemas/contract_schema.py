#backend/db/schemas/contract_schema.py
"""
Esquemas Pydantic para Contrato
"""
from datetime import datetime, date
from typing import Optional, Dict, Union
from decimal import Decimal
from pydantic import BaseModel, field_validator, ConfigDict

# Esquema base
class ContractBase(BaseModel):
    client_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    type: Optional[str] = None
    terms: Optional[str] = None
    
    @field_validator('start_date', 'end_date', mode='before')
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

# Esquema para crear contrato
class ContractCreate(ContractBase):
    pass

# Esquema para actualizar contrato
class ContractUpdate(BaseModel):
    client_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    type: Optional[str] = None
    terms: Optional[str] = None
    
    @field_validator('start_date', 'end_date', mode='before')
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
class ContractResponse(ContractBase):
    contract_id: int

    model_config = ConfigDict(from_attributes=True)

# Esquema con relaciones
class ContractWithRelations(ContractResponse):
    client: Optional[Dict] = None 