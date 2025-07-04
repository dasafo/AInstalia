#backend/db/crud/product_crud.py
"""
Operaciones CRUD para Producto
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from backend.models.product_model import Product
from backend.schemas.product_schema import ProductCreate, ProductUpdate
from backend.crud.base_crud import CRUDBase


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def __init__(self):
        super().__init__(Product)

    async def get(self, db: AsyncSession, sku: str) -> Optional[Product]:
        """Obtener producto por SKU"""
        return await super().get(db, id=sku)

    async def search_by_name(self, db: AsyncSession, *, name: str) -> List[Product]:
        """Buscar productos por nombre (búsqueda parcial)"""
        result = await db.execute(select(Product).filter(Product.name.ilike(f"%{name}%")))
        return result.scalars().all()

    async def search_by_description(self, db: AsyncSession, *, description: str) -> List[Product]:
        """Buscar productos por descripción (búsqueda parcial)"""
        result = await db.execute(select(Product).filter(Product.description.ilike(f"%{description}%")))
        return result.scalars().all()

    async def get_by_price_range(
        self, db: AsyncSession, *, min_price: Decimal, max_price: Decimal
    ) -> List[Product]:
        """Obtener productos en rango de precio"""
        result = await db.execute(select(Product).filter(
            Product.price >= min_price,
            Product.price <= max_price
        ))
        return result.scalars().all()

    async def get_with_specs(self, db: AsyncSession) -> List[Product]:
        """Obtener productos que tienen especificaciones JSON"""
        result = await db.execute(select(Product).filter(Product.spec_json.isnot(None)))
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, sku: str) -> Optional[Product]:
        """Eliminar producto por SKU"""
        return await super().remove(db, id=sku) 