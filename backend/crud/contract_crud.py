#backend/db/crud/contract_crud.py
"""
Operaciones CRUD para Contrato
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from backend.models.contract_model import Contract
from backend.schemas.contract_schema import ContractCreate, ContractUpdate
from backend.crud.base_crud import CRUDBase


class CRUDContract(CRUDBase[Contract, ContractCreate, ContractUpdate]):
    def __init__(self):
        super().__init__(Contract)

    def get(self, db: Session, contract_id: int) -> Optional[Contract]:
        """Obtener contrato por ID"""
        return db.query(Contract).filter(Contract.contract_id == contract_id).first()

    def get_by_client(self, db: Session, *, client_id: int, skip: int = 0, limit: int = 100) -> List[Contract]:
        """Obtener contratos de un cliente"""
        return db.query(Contract).filter(Contract.client_id == client_id).offset(skip).limit(limit).all()

    def get_by_type(self, db: Session, *, contract_type: str, skip: int = 0, limit: int = 100) -> List[Contract]:
        """Obtener contratos por tipo"""
        return db.query(Contract).filter(Contract.contract_type == contract_type).offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, *, status: str, skip: int = 0, limit: int = 100) -> List[Contract]:
        """Obtener contratos por estado"""
        return db.query(Contract).filter(Contract.status == status).offset(skip).limit(limit).all()

    def get_active_contracts(self, db: Session) -> List[Contract]:
        """Obtener contratos activos"""
        return db.query(Contract).filter(Contract.status == "activo").all()

    def get_expiring_contracts(self, db: Session, *, before_date: date) -> List[Contract]:
        """Obtener contratos que expiran antes de una fecha"""
        return db.query(Contract).filter(
            Contract.end_date <= before_date,
            Contract.status == "activo"
        ).all()

    def get_by_date_range(
        self, db: Session, *, start_date: date, end_date: date
    ) -> List[Contract]:
        """Obtener contratos que empiezan en rango de fechas"""
        return db.query(Contract).filter(
            Contract.start_date >= start_date,
            Contract.start_date <= end_date
        ).all()

    def remove(self, db: Session, *, contract_id: int) -> Contract:
        """Eliminar contrato por ID"""
        obj = db.query(Contract).filter(Contract.contract_id == contract_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj 