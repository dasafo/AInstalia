#backend/db/crud/technician_crud.py
"""
Operaciones CRUD para Técnico
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.technician_model import Technician
from backend.schemas.technician_schema import TechnicianCreate, TechnicianUpdate
from backend.crud.base_crud import CRUDBase


class CRUDTechnician(CRUDBase[Technician, TechnicianCreate, TechnicianUpdate]):
    def __init__(self):
        super().__init__(Technician)

    async def get(self, db: AsyncSession, technician_id: int) -> Optional[Technician]:
        """Obtener técnico por ID"""
        return await super().get(db, id=technician_id)

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[Technician]:
        """Obtener técnico por email"""
        result = await db.execute(select(Technician).filter(Technician.email == email))
        return result.scalars().first()

    async def get_by_specialization(self, db: AsyncSession, *, specialization: str) -> List[Technician]:
        """Obtener técnicos por especialización"""
        result = await db.execute(select(Technician).filter(Technician.specialization == specialization))
        return result.scalars().all()

    async def search_by_name(self, db: AsyncSession, *, name: str) -> List[Technician]:
        """Buscar técnicos por nombre (búsqueda parcial)"""
        result = await db.execute(select(Technician).filter(Technician.name.ilike(f"%{name}%")))
        return result.scalars().all()

    async def get_available_specializations(self, db: AsyncSession) -> List[str]:
        """Obtener lista de especializaciones disponibles"""
        result = await db.execute(select(Technician.specialization).distinct())
        specializations = result.scalars().all()
        return [spec for spec in specializations if spec is not None]

    async def remove(self, db: AsyncSession, *, technician_id: int) -> Optional[Technician]:
        """Eliminar técnico por ID"""
        return await super().remove(db, id=technician_id) 