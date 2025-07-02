#backend/api/v1/endpoints/stock.py
"""
Endpoints CRUD para stock
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.stock_schema import StockCreate, StockUpdate, StockResponse
from backend.crud import stock_crud

router = APIRouter()

@router.post("/", response_model=StockResponse)
async def create_stock(
    stock: StockCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo registro de stock"""
    return stock_crud.create(db=db, obj_in=stock)

@router.get("/", response_model=List[StockResponse])
async def read_stock(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    product_id: Optional[str] = Query(None, description="Filtrar por ID de producto"),
    warehouse_id: Optional[int] = Query(None, description="Filtrar por ID de almacén"),
    db: Session = Depends(get_db)
):
    """Obtener lista de stock con paginación y filtros opcionales"""
    if product_id and warehouse_id:
        # Filtrar por producto y almacén específicos
        stock_item = stock_crud.get_by_product_and_warehouse(db=db, product_id=product_id, warehouse_id=warehouse_id)
        return [stock_item] if stock_item else []
    elif product_id:
        # Filtrar solo por producto
        return stock_crud.get_by_product(db=db, product_id=product_id, skip=skip, limit=limit)
    elif warehouse_id:
        # Filtrar solo por almacén
        return stock_crud.get_by_warehouse(db=db, warehouse_id=warehouse_id, skip=skip, limit=limit)
    else:
        # Sin filtros, obtener todo
        return stock_crud.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{stock_id}", response_model=StockResponse)
async def read_stock_item(
    stock_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un registro de stock específico por ID"""
    stock_item = stock_crud.get(db=db, stock_id=stock_id)
    if not stock_item:
        raise HTTPException(status_code=404, detail="Registro de stock no encontrado")
    return stock_item

@router.put("/{stock_id}", response_model=StockResponse)
async def update_stock(
    stock_id: int,
    stock_update: StockUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un registro de stock existente"""
    stock_item = stock_crud.get(db=db, stock_id=stock_id)
    if not stock_item:
        raise HTTPException(status_code=404, detail="Registro de stock no encontrado")
    return stock_crud.update(db=db, db_obj=stock_item, obj_in=stock_update)

@router.delete("/{stock_id}", response_model=StockResponse)
async def delete_stock(
    stock_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar un registro de stock"""
    stock_item = stock_crud.get(db=db, stock_id=stock_id)
    if not stock_item:
        raise HTTPException(status_code=404, detail="Registro de stock no encontrado")
    return stock_crud.remove(db=db, stock_id=stock_id)