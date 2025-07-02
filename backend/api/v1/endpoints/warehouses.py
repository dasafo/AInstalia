#backend/api/v1/endpoints/warehouses.py
"""
Endpoints CRUD para almacenes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.warehouse_schema import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from backend.crud import warehouse_crud

router = APIRouter()

@router.post("/", response_model=WarehouseResponse)
async def create_warehouse(
    warehouse: WarehouseCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo almacén"""
    return warehouse_crud.create(db=db, obj_in=warehouse)

@router.get("/", response_model=List[WarehouseResponse])
async def read_warehouses(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db)
):
    """Obtener lista de almacenes con paginación"""
    return warehouse_crud.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def read_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un almacén específico por ID"""
    warehouse = warehouse_crud.get(db=db, warehouse_id=warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    return warehouse

@router.put("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: int,
    warehouse_update: WarehouseUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un almacén existente"""
    warehouse = warehouse_crud.get(db=db, warehouse_id=warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    return warehouse_crud.update(db=db, db_obj=warehouse, obj_in=warehouse_update)

@router.delete("/{warehouse_id}", response_model=WarehouseResponse)
async def delete_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar un almacén"""
    warehouse = warehouse_crud.get(db=db, warehouse_id=warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    return warehouse_crud.remove(db=db, warehouse_id=warehouse_id)