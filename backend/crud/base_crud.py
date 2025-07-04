#backend/db/crud/base_crud.py
"""
Base CRUD con operaciones genéricas
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Objeto CRUD con métodos CRUD por defecto para Create, Read, Update, Delete (CRUD).
        
        **Parámetros**
        * `model`: Clase modelo SQLAlchemy
        * `schema`: Esquema Pydantic
        """
        self.model = model
        self.primary_key_name = self.model.__table__.primary_key.columns[0].name

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Obtener registro por ID"""
        result = await db.execute(select(self.model).filter(getattr(self.model, self.primary_key_name) == id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Obtener múltiples registros con paginación"""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Crear nuevo registro"""
        if hasattr(obj_in, 'model_dump'):
            # Es un objeto Pydantic
            obj_in_data = obj_in.model_dump()
        else:
            # Es un diccionario
            obj_in_data = obj_in
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Actualizar registro existente"""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> ModelType:
        """Eliminar registro por ID"""
        result = await db.execute(select(self.model).filter(getattr(self.model, self.primary_key_name) == id))
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj 