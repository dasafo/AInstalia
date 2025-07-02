#backend/db/crud/client_crud.py
"""
Operaciones CRUD para Cliente
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.db.models.client_model import Client
from backend.db.schemas.client_schema import ClientCreate, ClientUpdate
from backend.db.crud.base_crud import CRUDBase


class CRUDClient(CRUDBase[Client, ClientCreate, ClientUpdate]):
    def __init__(self):
        super().__init__(Client)

    def get(self, db: Session, client_id: int) -> Optional[Client]:
        """Obtener cliente por ID"""
        return db.query(Client).filter(Client.client_id == client_id).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Client]:
        """Obtener cliente por email"""
        return db.query(Client).filter(Client.email == email).first()

    def get_by_company(self, db: Session, *, company_name: str) -> List[Client]:
        """Obtener clientes por nombre de empresa"""
        return db.query(Client).filter(Client.company_name == company_name).all()

    def search_by_name(self, db: Session, *, name: str) -> List[Client]:
        """Buscar clientes por nombre (búsqueda parcial)"""
        return db.query(Client).filter(Client.name.ilike(f"%{name}%")).all()

    def get_by_city(self, db: Session, *, city: str) -> List[Client]:
        """Obtener clientes por ciudad"""
        return db.query(Client).filter(Client.city == city).all()

    def remove(self, db: Session, *, client_id: int) -> Client:
        """Eliminar cliente por ID"""
        obj = db.query(Client).filter(Client.client_id == client_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj 