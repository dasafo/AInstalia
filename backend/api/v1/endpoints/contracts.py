#backend/api/v1/endpoints/contracts.py
"""
Endpoints CRUD para contratos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.crud import contract_crud
from backend.schemas.contract_schema import (
    ContractCreate,
    ContractUpdate,
    ContractResponse
)

router = APIRouter()

@router.post("/", response_model=ContractResponse)
async def create_contract(
    contract: ContractCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crear un nuevo contrato"""
    return await contract_crud.create(db=db, obj_in=contract)

@router.get("/", response_model=List[ContractResponse])
async def read_contracts(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    client_id: Optional[int] = Query(None, description="Filtrar por ID de cliente"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de contratos con paginación y filtros opcionales"""
    if client_id:
        return await contract_crud.get_by_client(db=db, client_id=client_id, skip=skip, limit=limit)
    elif status:
        return await contract_crud.get_by_status(db=db, status=status, skip=skip, limit=limit)
    else:
        return await contract_crud.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{contract_id}", response_model=ContractResponse)
async def read_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtener un contrato específico por ID"""
    contract = await contract_crud.get(db=db, contract_id=contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return contract

@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: str,
    contract_update: ContractUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar un contrato existente"""
    contract = await contract_crud.get(db=db, contract_id=contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return await contract_crud.update(db=db, db_obj=contract, obj_in=contract_update)

@router.delete("/{contract_id}", response_model=ContractResponse)
async def delete_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Eliminar un contrato"""
    contract = await contract_crud.get(db=db, contract_id=contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return await contract_crud.remove(db=db, contract_id=contract_id)