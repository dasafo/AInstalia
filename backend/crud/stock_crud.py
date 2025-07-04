#backend/db/crud/stock_crud.py
"""
Operaciones CRUD para Stock/Inventario
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.stock_model import Stock
from backend.schemas.stock_schema import StockCreate, StockUpdate
from backend.crud.base_crud import CRUDBase


class CRUDStock(CRUDBase[Stock, StockCreate, StockUpdate]):
    def __init__(self):
        super().__init__(Stock)

    async def get(self, db: AsyncSession, stock_id: int) -> Optional[Stock]:
        """Obtener stock por ID"""
        return await super().get(db, id=stock_id)

    async def get_by_sku_and_warehouse(
        self, db: AsyncSession, *, sku: str, warehouse_id: int
    ) -> Optional[Stock]:
        """Obtener stock específico por SKU y almacén"""
        result = await db.execute(select(Stock).filter(
            Stock.sku == sku,
            Stock.warehouse_id == warehouse_id
        ))
        return result.scalars().first()

    async def get_by_sku(self, db: AsyncSession, *, sku: str, skip: int = 0, limit: int = 100) -> List[Stock]:
        """Obtener todo el stock de un producto en todos los almacenes"""
        result = await db.execute(select(Stock).filter(Stock.sku == sku).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_warehouse(self, db: AsyncSession, *, warehouse_id: int, skip: int = 0, limit: int = 100) -> List[Stock]:
        """Obtener todo el stock de un almacén"""
        result = await db.execute(select(Stock).filter(Stock.warehouse_id == warehouse_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_low_stock(self, db: AsyncSession, *, min_quantity: int = 5) -> List[Stock]:
        """Obtener productos con stock bajo"""
        result = await db.execute(select(Stock).filter(Stock.quantity <= min_quantity))
        return result.scalars().all()

    async def get_out_of_stock(self, db: AsyncSession) -> List[Stock]:
        """Obtener productos sin stock"""
        result = await db.execute(select(Stock).filter(Stock.quantity == 0))
        return result.scalars().all()

    async def get_by_quantity_range(
        self, db: AsyncSession, *, min_quantity: int, max_quantity: int
    ) -> List[Stock]:
        """Obtener stock en rango de cantidad"""
        result = await db.execute(select(Stock).filter(
            Stock.quantity >= min_quantity,
            Stock.quantity <= max_quantity
        ))
        return result.scalars().all()

    async def get_by_product_and_warehouse(self, db: AsyncSession, *, product_id: str, warehouse_id: int) -> Optional[Stock]:
        """Obtener stock específico por producto y almacén"""
        result = await db.execute(select(Stock).filter(
            Stock.sku == product_id,
            Stock.warehouse_id == warehouse_id
        ))
        return result.scalars().first()

    async def get_by_product(self, db: AsyncSession, *, product_id: str, skip: int = 0, limit: int = 100) -> List[Stock]:
        """Obtener todo el stock de un producto en todos los almacenes"""
        result = await db.execute(select(Stock).filter(Stock.sku == product_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, stock_id: int) -> Optional[Stock]:
        """Eliminar registro de stock por ID"""
        return await super().remove(db, id=stock_id) 