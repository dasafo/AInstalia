#backend/db/crud/warehouse_crud.py
"""
Operaciones CRUD para Almacén
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.warehouse_model import Warehouse
from backend.schemas.warehouse_schema import WarehouseCreate, WarehouseUpdate
from backend.crud.base_crud import CRUDBase


class CRUDWarehouse(CRUDBase[Warehouse, WarehouseCreate, WarehouseUpdate]):
    def __init__(self):
        super().__init__(Warehouse)

    async def get(self, db: AsyncSession, warehouse_id: int) -> Optional[Warehouse]:
        """Obtener almacén por ID"""
        return await super().get(db, id=warehouse_id)

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Warehouse]:
        """Obtener almacén por nombre"""
        result = await db.execute(select(Warehouse).filter(Warehouse.name == name))
        return result.scalars().first()

    async def search_by_name(self, db: AsyncSession, *, name: str) -> List[Warehouse]:
        """Buscar almacenes por nombre (búsqueda parcial)"""
        result = await db.execute(select(Warehouse).filter(Warehouse.name.ilike(f"%{name}%")))
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, warehouse_id: int) -> Optional[Warehouse]:
        """Eliminar almacén por ID"""
        return await super().remove(db, id=warehouse_id) 