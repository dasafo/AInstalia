#backend/db/crud/product_crud.py
"""
Operaciones CRUD para Producto
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from decimal import Decimal

from backend.models.product_model import Product
from backend.schemas.product_schema import ProductCreate, ProductUpdate
from backend.crud.base_crud import CRUDBase


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def __init__(self):
        super().__init__(Product)

    def get(self, db: Session, sku: str) -> Optional[Product]:
        """Obtener producto por SKU"""
        return db.query(Product).filter(Product.sku == sku).first()

    def search_by_name(self, db: Session, *, name: str) -> List[Product]:
        """Buscar productos por nombre (búsqueda parcial)"""
        return db.query(Product).filter(Product.name.ilike(f"%{name}%")).all()

    def search_by_description(self, db: Session, *, description: str) -> List[Product]:
        """Buscar productos por descripción (búsqueda parcial)"""
        return db.query(Product).filter(Product.description.ilike(f"%{description}%")).all()

    def get_by_price_range(
        self, db: Session, *, min_price: Decimal, max_price: Decimal
    ) -> List[Product]:
        """Obtener productos en rango de precio"""
        return db.query(Product).filter(
            Product.price >= min_price,
            Product.price <= max_price
        ).all()

    def get_with_specs(self, db: Session) -> List[Product]:
        """Obtener productos que tienen especificaciones JSON"""
        return db.query(Product).filter(Product.spec_json.isnot(None)).all()

    def remove(self, db: Session, *, sku: str) -> Product:
        """Eliminar producto por SKU"""
        obj = db.query(Product).filter(Product.sku == sku).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj 