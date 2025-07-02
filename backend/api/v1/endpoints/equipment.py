#backend/api/v1/endpoints/equipment.py
"""
Endpoints CRUD para equipos instalados
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.crud import equipment_crud
from backend.schemas.equipment_schema import (
    InstalledEquipmentCreate,
    InstalledEquipmentUpdate,
    InstalledEquipmentResponse
)

router = APIRouter()

@router.post("/", response_model=InstalledEquipmentResponse)
async def create_equipment(
    equipment: InstalledEquipmentCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo registro de equipo instalado"""
    return equipment_crud.create(db=db, obj_in=equipment)

@router.get("/", response_model=List[InstalledEquipmentResponse])
async def read_equipment(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db)
):
    """Obtener lista de equipos instalados con paginación"""
    return equipment_crud.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{equipment_id}", response_model=InstalledEquipmentResponse)
async def read_equipment_item(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un equipo instalado específico por ID"""
    equipment = equipment_crud.get(db=db, id=equipment_id)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipo instalado no encontrado")
    return equipment

@router.put("/{equipment_id}", response_model=InstalledEquipmentResponse)
async def update_equipment(
    equipment_id: int,
    equipment_update: InstalledEquipmentUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un equipo instalado existente"""
    equipment = equipment_crud.get(db=db, id=equipment_id)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipo instalado no encontrado")
    
    return equipment_crud.update(db=db, db_obj=equipment, obj_in=equipment_update)

@router.delete("/{equipment_id}", response_model=InstalledEquipmentResponse)
async def delete_equipment(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar un equipo instalado"""
    equipment = equipment_crud.delete(db=db, id=equipment_id)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipo instalado no encontrado")
    return equipment