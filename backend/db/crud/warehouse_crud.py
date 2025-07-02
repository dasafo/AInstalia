#backend/db/crud/warehouse_crud.py
"""
Operaciones CRUD para Almacén
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.db.models.warehouse_model import Warehouse
from backend.db.schemas.warehouse_schema import WarehouseCreate, WarehouseUpdate
from backend.db.crud.base_crud import CRUDBase


class CRUDWarehouse(CRUDBase[Warehouse, WarehouseCreate, WarehouseUpdate]):
    def __init__(self):
        super().__init__(Warehouse)

    def get(self, db: Session, warehouse_id: int) -> Optional[Warehouse]:
        """Obtener almacén por ID"""
        return db.query(Warehouse).filter(Warehouse.warehouse_id == warehouse_id).first()

    def get_by_name(self, db: Session, *, name: str) -> Optional[Warehouse]:
        """Obtener almacén por nombre"""
        return db.query(Warehouse).filter(Warehouse.name == name).first()

    def search_by_name(self, db: Session, *, name: str) -> List[Warehouse]:
        """Buscar almacenes por nombre (búsqueda parcial)"""
        return db.query(Warehouse).filter(Warehouse.name.ilike(f"%{name}%")).all()

    def remove(self, db: Session, *, warehouse_id: int) -> Warehouse:
        """Eliminar almacén por ID"""
        obj = db.query(Warehouse).filter(Warehouse.warehouse_id == warehouse_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj 