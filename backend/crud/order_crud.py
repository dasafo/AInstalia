#backend/db/crud/order_crud.py
"""
Operaciones CRUD para Pedido y Elementos de Pedido
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from decimal import Decimal

from backend.models.order_model import Order, OrderItem
from backend.schemas.order_schema import OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate
from backend.crud.base_crud import CRUDBase


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def __init__(self):
        super().__init__(Order)

    def get(self, db: Session, order_id: str) -> Optional[Order]:
        """Obtener pedido por ID"""
        return db.query(Order).filter(Order.order_id == order_id).first()

    def get_by_client(self, db: Session, *, client_id: int) -> List[Order]:
        """Obtener pedidos de un cliente"""
        return db.query(Order).filter(Order.client_id == client_id).all()

    def get_by_chat(self, db: Session, *, chat_id: str) -> List[Order]:
        """Obtener pedidos de un chat"""
        return db.query(Order).filter(Order.chat_id == chat_id).all()

    def get_by_status(self, db: Session, *, status: str) -> List[Order]:
        """Obtener pedidos por estado"""
        return db.query(Order).filter(Order.status == status).all()

    def get_pending_orders(self, db: Session) -> List[Order]:
        """Obtener pedidos pendientes"""
        return db.query(Order).filter(Order.status == "pendiente").all()

    def get_by_amount_range(
        self, db: Session, *, min_amount: Decimal, max_amount: Decimal
    ) -> List[Order]:
        """Obtener pedidos en rango de monto"""
        return db.query(Order).filter(
            Order.total_amount >= min_amount,
            Order.total_amount <= max_amount
        ).all()

    def remove(self, db: Session, *, order_id: str) -> Order:
        """Eliminar pedido por ID"""
        obj = db.query(Order).filter(Order.order_id == order_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj


class CRUDOrderItem(CRUDBase[OrderItem, OrderItemCreate, OrderItemUpdate]):
    def __init__(self):
        super().__init__(OrderItem)

    def get(self, db: Session, item_id: int) -> Optional[OrderItem]:
        """Obtener elemento de pedido por ID"""
        return db.query(OrderItem).filter(OrderItem.item_id == item_id).first()

    def get_by_order(self, db: Session, *, order_id: str) -> List[OrderItem]:
        """Obtener elementos de un pedido"""
        return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    def get_by_product(self, db: Session, *, product_sku: str) -> List[OrderItem]:
        """Obtener elementos que contienen un producto específico"""
        return db.query(OrderItem).filter(OrderItem.product_sku == product_sku).all()

    def get_by_quantity_range(
        self, db: Session, *, min_quantity: int, max_quantity: int
    ) -> List[OrderItem]:
        """Obtener elementos en rango de cantidad"""
        return db.query(OrderItem).filter(
            OrderItem.quantity >= min_quantity,
            OrderItem.quantity <= max_quantity
        ).all()

    def remove(self, db: Session, *, item_id: int) -> OrderItem:
        """Eliminar elemento de pedido por ID"""
        obj = db.query(OrderItem).filter(OrderItem.item_id == item_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj 