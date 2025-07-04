#backend/db/crud/equipment_crud.py
"""
Operaciones CRUD para Equipo Instalado
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.equipment_model import InstalledEquipment
from backend.schemas.equipment_schema import InstalledEquipmentCreate, InstalledEquipmentUpdate
from backend.crud.base_crud import CRUDBase


class CRUDInstalledEquipment(CRUDBase[InstalledEquipment, InstalledEquipmentCreate, InstalledEquipmentUpdate]):
    def __init__(self):
        super().__init__(InstalledEquipment)

    async def get(self, db: AsyncSession, equipment_id: int) -> Optional[InstalledEquipment]:
        """Obtener equipo por ID"""
        return await super().get(db, id=equipment_id)

    async def get_by_client(self, db: AsyncSession, *, client_id: int) -> List[InstalledEquipment]:
        """Obtener equipos instalados de un cliente"""
        result = await db.execute(select(InstalledEquipment).filter(InstalledEquipment.client_id == client_id))
        return result.scalars().all()

    async def get_by_sku(self, db: AsyncSession, *, sku: str) -> List[InstalledEquipment]:
        """Obtener equipos por SKU de producto"""
        result = await db.execute(select(InstalledEquipment).filter(InstalledEquipment.sku == sku))
        return result.scalars().all()

    async def get_by_status(self, db: AsyncSession, *, status: str) -> List[InstalledEquipment]:
        """Obtener equipos por estado"""
        result = await db.execute(select(InstalledEquipment).filter(InstalledEquipment.status == status))
        return result.scalars().all()

    async def get_by_date_range(
        self, db: AsyncSession, *, start_date: date, end_date: date
    ) -> List[InstalledEquipment]:
        """Obtener equipos instalados en rango de fechas"""
        result = await db.execute(select(InstalledEquipment).filter(
            InstalledEquipment.installation_date >= start_date,
            InstalledEquipment.installation_date <= end_date
        ))
        return result.scalars().all()

    async def get_active_equipment(self, db: AsyncSession) -> List[InstalledEquipment]:
        """Obtener equipos activos"""
        result = await db.execute(select(InstalledEquipment).filter(InstalledEquipment.status == "activo"))
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, equipment_id: int) -> Optional[InstalledEquipment]:
        """Eliminar equipo por ID"""
        return await super().remove(db, id=equipment_id) 