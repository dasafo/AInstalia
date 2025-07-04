#backend/api/v1/endpoints/orders.py
"""
Endpoints CRUD para pedidos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.crud import order_crud
from backend.schemas.order_schema import (
    OrderCreate,
    OrderUpdate,
    OrderResponse
)

router = APIRouter()

@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crear un nuevo pedido"""
    return await order_crud.create(db=db, obj_in=order)

@router.get("/", response_model=List[OrderResponse])
async def read_orders(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de pedidos con paginación"""
    return await order_crud.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtener un pedido específico por ID"""
    order = await order_crud.get(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return order

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar un pedido existente"""
    order = await order_crud.get(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return await order_crud.update(db=db, db_obj=order, obj_in=order_update)

@router.delete("/{order_id}", response_model=OrderResponse)
async def delete_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Eliminar un pedido"""
    order = await order_crud.get(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return await order_crud.remove(db=db, order_id=order_id)