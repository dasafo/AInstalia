#backend/db/crud/order_crud.py
"""
Operaciones CRUD para Pedido y Elementos de Pedido
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from backend.models.order_model import Order, OrderItem
from backend.schemas.order_schema import OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate
from backend.crud.base_crud import CRUDBase


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def __init__(self):
        super().__init__(Order)

    async def get(self, db: AsyncSession, order_id: str) -> Optional[Order]:
        """Obtener pedido por ID"""
        return await super().get(db, id=order_id)

    async def get_by_client(self, db: AsyncSession, *, client_id: int) -> List[Order]:
        """Obtener pedidos de un cliente"""
        result = await db.execute(select(Order).filter(Order.client_id == client_id))
        return result.scalars().all()

    async def get_by_chat(self, db: AsyncSession, *, chat_id: str) -> List[Order]:
        """Obtener pedidos de un chat"""
        result = await db.execute(select(Order).filter(Order.chat_id == chat_id))
        return result.scalars().all()

    async def get_by_status(self, db: AsyncSession, *, status: str) -> List[Order]:
        """Obtener pedidos por estado"""
        result = await db.execute(select(Order).filter(Order.status == status))
        return result.scalars().all()

    async def get_pending_orders(self, db: AsyncSession) -> List[Order]:
        """Obtener pedidos pendientes"""
        result = await db.execute(select(Order).filter(Order.status == "pendiente"))
        return result.scalars().all()

    async def get_by_amount_range(
        self, db: AsyncSession, *, min_amount: Decimal, max_amount: Decimal
    ) -> List[Order]:
        """Obtener pedidos en rango de monto"""
        result = await db.execute(select(Order).filter(
            Order.total_amount >= min_amount,
            Order.total_amount <= max_amount
        ))
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, order_id: str) -> Optional[Order]:
        """Eliminar pedido por ID"""
        return await super().remove(db, id=order_id)


class CRUDOrderItem(CRUDBase[OrderItem, OrderItemCreate, OrderItemUpdate]):
    def __init__(self):
        super().__init__(OrderItem)

    async def get(self, db: AsyncSession, item_id: int) -> Optional[OrderItem]:
        """Obtener elemento de pedido por ID"""
        return await super().get(db, id=item_id)

    async def get_by_order(self, db: AsyncSession, *, order_id: str) -> List[OrderItem]:
        """Obtener elementos de un pedido"""
        result = await db.execute(select(OrderItem).filter(OrderItem.order_id == order_id))
        return result.scalars().all()

    async def get_by_product(self, db: AsyncSession, *, product_sku: str) -> List[OrderItem]:
        """Obtener elementos que contienen un producto específico"""
        result = await db.execute(select(OrderItem).filter(OrderItem.product_sku == product_sku))
        return result.scalars().all()

    async def get_by_quantity_range(
        self, db: AsyncSession, *, min_quantity: int, max_quantity: int
    ) -> List[OrderItem]:
        """Obtener elementos en rango de cantidad"""
        result = await db.execute(select(OrderItem).filter(
            OrderItem.quantity >= min_quantity,
            OrderItem.quantity <= max_quantity
        ))
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, item_id: int) -> Optional[OrderItem]:
        """Eliminar elemento de pedido por ID"""
        return await super().remove(db, id=item_id) 