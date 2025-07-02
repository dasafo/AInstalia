#backend/db/crud/stock_crud.py
"""
Operaciones CRUD para Stock/Inventario
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.db.models.stock_model import Stock
from backend.db.schemas.stock_schema import StockCreate, StockUpdate
from backend.db.crud.base_crud import CRUDBase


class CRUDStock(CRUDBase[Stock, StockCreate, StockUpdate]):
    def __init__(self):
        super().__init__(Stock)

    def get(self, db: Session, stock_id: int) -> Optional[Stock]:
        """Obtener stock por ID"""
        return db.query(Stock).filter(Stock.stock_id == stock_id).first()

    def get_by_sku_and_warehouse(
        self, db: Session, *, sku: str, warehouse_id: int
    ) -> Optional[Stock]:
        """Obtener stock específico por SKU y almacén"""
        return db.query(Stock).filter(
            Stock.sku == sku,
            Stock.warehouse_id == warehouse_id
        ).first()

    def get_by_sku(self, db: Session, *, sku: str) -> List[Stock]:
        """Obtener todo el stock de un producto en todos los almacenes"""
        return db.query(Stock).filter(Stock.sku == sku).all()

    def get_by_warehouse(self, db: Session, *, warehouse_id: int) -> List[Stock]:
        """Obtener todo el stock de un almacén"""
        return db.query(Stock).filter(Stock.warehouse_id == warehouse_id).all()

    def get_low_stock(self, db: Session, *, min_quantity: int = 5) -> List[Stock]:
        """Obtener productos con stock bajo"""
        return db.query(Stock).filter(Stock.quantity <= min_quantity).all()

    def get_out_of_stock(self, db: Session) -> List[Stock]:
        """Obtener productos sin stock"""
        return db.query(Stock).filter(Stock.quantity == 0).all()

    def get_by_quantity_range(
        self, db: Session, *, min_quantity: int, max_quantity: int
    ) -> List[Stock]:
        """Obtener stock en rango de cantidad"""
        return db.query(Stock).filter(
            Stock.quantity >= min_quantity,
            Stock.quantity <= max_quantity
        ).all()

    def remove(self, db: Session, *, stock_id: int) -> Stock:
        """Eliminar registro de stock por ID"""
        obj = db.query(Stock).filter(Stock.stock_id == stock_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj 