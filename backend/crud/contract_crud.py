#backend/db/crud/contract_crud.py
"""
Operaciones CRUD para Contrato
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.contract_model import Contract
from backend.schemas.contract_schema import ContractCreate, ContractUpdate
from backend.crud.base_crud import CRUDBase


class CRUDContract(CRUDBase[Contract, ContractCreate, ContractUpdate]):
    def __init__(self):
        super().__init__(Contract)

    async def get(self, db: AsyncSession, contract_id: int) -> Optional[Contract]:
        """Obtener contrato por ID"""
        return await super().get(db, id=contract_id)

    async def get_by_client(self, db: AsyncSession, *, client_id: int, skip: int = 0, limit: int = 100) -> List[Contract]:
        """Obtener contratos de un cliente"""
        result = await db.execute(select(Contract).filter(Contract.client_id == client_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_type(self, db: AsyncSession, *, contract_type: str, skip: int = 0, limit: int = 100) -> List[Contract]:
        """Obtener contratos por tipo"""
        result = await db.execute(select(Contract).filter(Contract.contract_type == contract_type).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_status(self, db: AsyncSession, *, status: str, skip: int = 0, limit: int = 100) -> List[Contract]:
        """Obtener contratos por estado"""
        result = await db.execute(select(Contract).filter(Contract.status == status).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_active_contracts(self, db: AsyncSession) -> List[Contract]:
        """Obtener contratos activos"""
        result = await db.execute(select(Contract).filter(Contract.status == "activo"))
        return result.scalars().all()

    async def get_expiring_contracts(self, db: AsyncSession, *, before_date: date) -> List[Contract]:
        """Obtener contratos que expiran antes de una fecha"""
        result = await db.execute(select(Contract).filter(
            Contract.end_date <= before_date,
            Contract.status == "activo"
        ))
        return result.scalars().all()

    async def get_by_date_range(
        self, db: AsyncSession, *, start_date: date, end_date: date
    ) -> List[Contract]:
        """Obtener contratos que empiezan en rango de fechas"""
        result = await db.execute(select(Contract).filter(
            Contract.start_date >= start_date,
            Contract.start_date <= end_date
        ))
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, contract_id: int) -> Optional[Contract]:
        """Eliminar contrato por ID"""
        return await super().remove(db, id=contract_id)