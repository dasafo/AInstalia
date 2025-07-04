#backend/db/crud/client_crud.py
"""
Operaciones CRUD para Cliente
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.client_model import Client
from backend.schemas.client_schema import ClientCreate, ClientUpdate
from backend.crud.base_crud import CRUDBase


class CRUDClient(CRUDBase[Client, ClientCreate, ClientUpdate]):
    def __init__(self):
        super().__init__(Client)

    async def get(self, db: AsyncSession, client_id: int) -> Optional[Client]:
        """Obtener cliente por ID"""
        return await super().get(db, id=client_id)

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[Client]:
        """Obtener cliente por email"""
        result = await db.execute(select(Client).filter(Client.email == email))
        return result.scalars().first()

    async def get_by_company(self, db: AsyncSession, *, company_name: str) -> List[Client]:
        """Obtener clientes por nombre de empresa"""
        result = await db.execute(select(Client).filter(Client.company_name == company_name))
        return result.scalars().all()

    async def search_by_name(self, db: AsyncSession, *, name: str) -> List[Client]:
        """Buscar clientes por nombre (búsqueda parcial)"""
        result = await db.execute(select(Client).filter(Client.name.ilike(f"%{name}%")))
        return result.scalars().all()

    async def get_by_city(self, db: AsyncSession, *, city: str) -> List[Client]:
        """Obtener clientes por ciudad"""
        result = await db.execute(select(Client).filter(Client.city == city))
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, client_id: int) -> Optional[Client]:
        """Eliminar cliente por ID"""
        return await super().remove(db, id=client_id) 