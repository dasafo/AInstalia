#backend/api/v1/endpoints/clients.py

"""
Endpoints CRUD para clientes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.schemas.client_schema import ClientCreate, ClientUpdate, ClientResponse
from backend.crud import client_crud

router = APIRouter()

@router.post("/", response_model=ClientResponse)
async def create_client(
    client: ClientCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crear un nuevo cliente"""
    return await client_crud.create(db=db, obj_in=client)

@router.get("/", response_model=List[ClientResponse])
async def read_clients(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de clientes con paginación"""
    return await client_crud.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{client_id}", response_model=ClientResponse)
async def read_client(
    client_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtener un cliente específico por ID"""
    client = await client_crud.get(db=db, client_id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_update: ClientUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar un cliente existente"""
    client = await client_crud.get(db=db, client_id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return await client_crud.update(db=db, db_obj=client, obj_in=client_update)

@router.delete("/{client_id}", response_model=ClientResponse)
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Eliminar un cliente"""
    client = await client_crud.get(db=db, client_id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return await client_crud.remove(db=db, client_id=client_id)