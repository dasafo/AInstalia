#backend/api/v1/endpoints/interventions.py
"""
Endpoints CRUD para intervenciones
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.crud import intervention_crud
from backend.schemas.intervention_schema import (
    InterventionCreate,
    InterventionUpdate,
    InterventionResponse
)

router = APIRouter()

@router.post("/", response_model=InterventionResponse)
async def create_intervention(
    intervention: InterventionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crear una nueva intervención"""
    return await intervention_crud.create(db=db, obj_in=intervention)

@router.get("/", response_model=List[InterventionResponse])
async def read_interventions(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    technician_id: Optional[int] = Query(None, description="Filtrar por ID de técnico"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de intervenciones con paginación y filtros opcionales"""
    if technician_id:
        return await intervention_crud.get_by_technician(db=db, technician_id=technician_id, skip=skip, limit=limit)
    elif status:
        return await intervention_crud.get_by_status(db=db, status=status, skip=skip, limit=limit)
    else:
        return await intervention_crud.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{intervention_id}", response_model=InterventionResponse)
async def read_intervention(
    intervention_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtener una intervención específica por ID"""
    intervention = await intervention_crud.get(db=db, intervention_id=intervention_id)
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervención no encontrada")
    return intervention

@router.put("/{intervention_id}", response_model=InterventionResponse)
async def update_intervention(
    intervention_id: str,
    intervention_update: InterventionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar una intervención existente"""
    intervention = await intervention_crud.get(db=db, intervention_id=intervention_id)
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervención no encontrada")
    return await intervention_crud.update(db=db, db_obj=intervention, obj_in=intervention_update)

@router.delete("/{intervention_id}", response_model=InterventionResponse)
async def delete_intervention(
    intervention_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Eliminar una intervención"""
    intervention = await intervention_crud.get(db=db, intervention_id=intervention_id)
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervención no encontrada")
    return await intervention_crud.remove(db=db, intervention_id=intervention_id)