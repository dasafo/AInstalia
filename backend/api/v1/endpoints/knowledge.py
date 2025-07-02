#backend/api/v1/endpoints/knowledge.py
"""
Endpoints CRUD para feedback de conocimiento
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.crud import knowledge_feedback_crud
from backend.schemas.knowledge_feedback_schema import (
    KnowledgeFeedbackCreate,
    KnowledgeFeedbackUpdate,
    KnowledgeFeedbackResponse,
    UserType,
    FeedbackStatus
)

router = APIRouter()

@router.post("/", response_model=KnowledgeFeedbackResponse)
async def create_knowledge_feedback(
    feedback: KnowledgeFeedbackCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo feedback de conocimiento"""
    return knowledge_feedback_crud.create(db=db, obj_in=feedback)

@router.get("/", response_model=List[KnowledgeFeedbackResponse])
async def read_knowledge_feedback(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    user_type: Optional[str] = Query(None, description="Filtrar por tipo de usuario"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """Obtener lista de feedback de conocimiento con paginación y filtros opcionales"""
    if user_type and status:
        return knowledge_feedback_crud.get_by_user_type_and_status(db=db, user_type=user_type, status=status, skip=skip, limit=limit)
    elif user_type:
        return knowledge_feedback_crud.get_by_user_type(db=db, user_type=user_type, skip=skip, limit=limit)
    elif status:
        return knowledge_feedback_crud.get_by_status(db=db, status=status, skip=skip, limit=limit)
    else:
        return knowledge_feedback_crud.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{feedback_id}", response_model=KnowledgeFeedbackResponse)
async def read_knowledge_feedback_item(
    feedback_id: str,
    db: Session = Depends(get_db)
):
    """Obtener un feedback de conocimiento específico por ID"""
    feedback = knowledge_feedback_crud.get(db=db, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback de conocimiento no encontrado")
    return feedback

@router.put("/{feedback_id}", response_model=KnowledgeFeedbackResponse)
async def update_knowledge_feedback(
    feedback_id: str,
    feedback_update: KnowledgeFeedbackUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un feedback de conocimiento existente"""
    feedback = knowledge_feedback_crud.get(db=db, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback de conocimiento no encontrado")
    return knowledge_feedback_crud.update(db=db, db_obj=feedback, obj_in=feedback_update)

@router.delete("/{feedback_id}", response_model=KnowledgeFeedbackResponse)
async def delete_knowledge_feedback(
    feedback_id: str,
    db: Session = Depends(get_db)
):
    """Eliminar un feedback de conocimiento"""
    feedback = knowledge_feedback_crud.get(db=db, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback de conocimiento no encontrado")
    return knowledge_feedback_crud.remove(db=db, feedback_id=feedback_id)