#backend/api/v1/endpoints/technicians.py
"""
Endpoints CRUD para técnicos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.crud import technician_crud
from backend.schemas.technician_schema import (
    TechnicianCreate,
    TechnicianUpdate,
    TechnicianResponse
)

router = APIRouter()

@router.post("/", response_model=TechnicianResponse)
async def create_technician(
    technician: TechnicianCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo técnico"""
    return technician_crud.create(db=db, obj_in=technician)

@router.get("/", response_model=List[TechnicianResponse])
async def read_technicians(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db)
):
    """Obtener lista de técnicos con paginación"""
    return technician_crud.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{technician_id}", response_model=TechnicianResponse)
async def read_technician(
    technician_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un técnico específico por ID"""
    technician = technician_crud.get(db=db, technician_id=technician_id)
    if not technician:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    return technician

@router.put("/{technician_id}", response_model=TechnicianResponse)
async def update_technician(
    technician_id: int,
    technician_update: TechnicianUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un técnico existente"""
    technician = technician_crud.get(db=db, technician_id=technician_id)
    if not technician:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    return technician_crud.update(db=db, db_obj=technician, obj_in=technician_update)

@router.delete("/{technician_id}", response_model=TechnicianResponse)
async def delete_technician(
    technician_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar un técnico"""
    technician = technician_crud.get(db=db, technician_id=technician_id)
    if not technician:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    return technician_crud.remove(db=db, technician_id=technician_id)