#backend/db/crud/intervention_crud.py
"""
Operaciones CRUD para Intervención
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.intervention_model import Intervention
from backend.schemas.intervention_schema import InterventionCreate, InterventionUpdate
from backend.crud.base_crud import CRUDBase


class CRUDIntervention(CRUDBase[Intervention, InterventionCreate, InterventionUpdate]):
    def __init__(self):
        super().__init__(Intervention)

    async def get(self, db: AsyncSession, intervention_id: int) -> Optional[Intervention]:
        """Obtener intervención por ID"""
        return await super().get(db, id=intervention_id)

    async def get_by_client(self, db: AsyncSession, *, client_id: int, skip: int = 0, limit: int = 100) -> List[Intervention]:
        """Obtener intervenciones de un cliente"""
        result = await db.execute(select(Intervention).filter(Intervention.client_id == client_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_technician(self, db: AsyncSession, *, technician_id: int, skip: int = 0, limit: int = 100) -> List[Intervention]:
        """Obtener intervenciones de un técnico"""
        result = await db.execute(select(Intervention).filter(Intervention.technician_id == technician_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_equipment(self, db: AsyncSession, *, equipment_id: int, skip: int = 0, limit: int = 100) -> List[Intervention]:
        """Obtener intervenciones de un equipo"""
        result = await db.execute(select(Intervention).filter(Intervention.equipment_id == equipment_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_status(self, db: AsyncSession, *, status: str, skip: int = 0, limit: int = 100) -> List[Intervention]:
        """Obtener intervenciones por estado"""
        result = await db.execute(select(Intervention).filter(Intervention.status == status).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_date_range(
        self, db: AsyncSession, *, start_date: date, end_date: date
    ) -> List[Intervention]:
        """Obtener intervenciones en rango de fechas"""
        result = await db.execute(select(Intervention).filter(
            Intervention.intervention_date >= start_date,
            Intervention.intervention_date <= end_date
        ))
        return result.scalars().all()

    async def get_pending_interventions(self, db: AsyncSession) -> List[Intervention]:
        """Obtener intervenciones pendientes"""
        result = await db.execute(select(Intervention).filter(Intervention.status == "pendiente"))
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, intervention_id: int) -> Optional[Intervention]:
        """Eliminar intervención por ID"""
        return await super().remove(db, id=intervention_id) 