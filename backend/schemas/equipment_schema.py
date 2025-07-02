#backend/db/schemas/equipment_schema.py
"""
Esquemas Pydantic para Equipo Instalado
"""
from datetime import datetime, date
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

# Esquema base
class InstalledEquipmentBase(BaseModel):
    client_id: int
    sku: str
    install_date: date  # Coincidir con SQL: install_date
    status: str = "activo"
    config_json: Optional[Dict[str, Any]] = None

# Esquema para crear equipo instalado
class InstalledEquipmentCreate(InstalledEquipmentBase):
    pass

# Esquema para actualizar equipo instalado
class InstalledEquipmentUpdate(BaseModel):
    client_id: Optional[int] = None
    sku: Optional[str] = None
    install_date: Optional[date] = None
    status: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None

# Esquema de respuesta
class InstalledEquipmentResponse(InstalledEquipmentBase):
    equipment_id: int

    model_config = ConfigDict(from_attributes=True)

# Esquema con relaciones
class InstalledEquipmentWithRelations(InstalledEquipmentResponse):
    client: Optional[Dict] = None
    product: Optional[Dict] = None 