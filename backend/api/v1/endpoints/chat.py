#backend/api/v1/endpoints/chat.py
"""
Endpoints CRUD para sesiones y mensajes de chat
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.crud import chat_session_crud, chat_message_crud
from backend.schemas.chat_session_schema import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse
)
from backend.schemas.chat_message_schema import (
    ChatMessageCreate,
    ChatMessageUpdate,
    ChatMessageResponse
)

router = APIRouter()

# Endpoints para sesiones de chat
@router.post("/sessions/", response_model=ChatSessionResponse)
async def create_chat_session(
    session: ChatSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crear una nueva sesión de chat"""
    return await chat_session_crud.create(db=db, obj_in=session)

@router.get("/sessions/", response_model=List[ChatSessionResponse])
async def read_chat_sessions(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de sesiones de chat con paginación"""
    return await chat_session_crud.get_multi(db=db, skip=skip, limit=limit)

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def read_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtener una sesión de chat específica por ID"""
    session = await chat_session_crud.get(db=db, chat_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión de chat no encontrada")
    return session

@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: str,
    session_update: ChatSessionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar una sesión de chat existente"""
    session = await chat_session_crud.get(db=db, chat_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión de chat no encontrada")
    return await chat_session_crud.update(db=db, db_obj=session, obj_in=session_update)

@router.delete("/sessions/{session_id}", response_model=ChatSessionResponse)
async def delete_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Eliminar una sesión de chat"""
    session = await chat_session_crud.get(db=db, chat_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión de chat no encontrada")
    return await chat_session_crud.remove(db=db, chat_id=session_id)

# Endpoints para mensajes de chat
@router.post("/messages/", response_model=ChatMessageResponse)
async def create_chat_message(
    message: ChatMessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crear un nuevo mensaje de chat"""
    return await chat_message_crud.create(db=db, obj_in=message)

@router.get("/messages/", response_model=List[ChatMessageResponse])
async def read_chat_messages(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    session_id: Optional[str] = Query(None, description="Filtrar por ID de sesión"),
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de mensajes de chat con paginación y filtros opcionales"""
    if session_id:
        return await chat_message_crud.get_by_chat(db=db, chat_id=session_id)
    else:
        return await chat_message_crud.get_multi(db=db, skip=skip, limit=limit)

@router.get("/messages/session/{chat_id}", response_model=List[ChatMessageResponse])
async def read_chat_messages_by_session(
    chat_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtener todos los mensajes de una sesión de chat específica"""
    messages = await chat_message_crud.get_by_chat(db=db, chat_id=chat_id)
    if not messages:
        raise HTTPException(status_code=404, detail="No se encontraron mensajes para esta sesión")
    return messages

@router.get("/messages/{message_id}", response_model=ChatMessageResponse)
async def read_chat_message(
    message_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtener un mensaje de chat específico por ID"""
    message = await chat_message_crud.get(db=db, message_id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje de chat no encontrado")
    return message

@router.put("/messages/{message_id}", response_model=ChatMessageResponse)
async def update_chat_message(
    message_id: int,
    message_update: ChatMessageUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar un mensaje de chat existente"""
    message = await chat_message_crud.get(db=db, message_id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje de chat no encontrado")
    return await chat_message_crud.update(db=db, db_obj=message, obj_in=message_update)

@router.delete("/messages/{message_id}", response_model=ChatMessageResponse)
async def delete_chat_message(
    message_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Eliminar un mensaje de chat"""
    message = await chat_message_crud.get(db=db, message_id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje de chat no encontrado")
    return await chat_message_crud.remove(db=db, message_id=message_id)