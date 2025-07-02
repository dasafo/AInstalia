#backend/api/v1/endpoints/products.py
"""
Endpoints CRUD para productos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from backend.crud import product_crud

router = APIRouter()

@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo producto"""
    return product_crud.create(db=db, obj_in=product)

@router.get("/", response_model=List[ProductResponse])
async def read_products(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db)
):
    """Obtener lista de productos con paginación"""
    return product_crud.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Obtener un producto específico por SKU"""
    product = product_crud.get(db=db, sku=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un producto existente"""
    product = product_crud.get(db=db, sku=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product_crud.update(db=db, db_obj=product, obj_in=product_update)

@router.delete("/{product_id}", response_model=ProductResponse)
async def delete_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Eliminar un producto"""
    product = product_crud.get(db=db, sku=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product_crud.remove(db=db, sku=product_id)