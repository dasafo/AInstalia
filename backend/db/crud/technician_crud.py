#backend/db/crud/technician_crud.py
"""
Operaciones CRUD para Técnico
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.db.models.technician_model import Technician
from backend.db.schemas.technician_schema import TechnicianCreate, TechnicianUpdate
from backend.db.crud.base_crud import CRUDBase


class CRUDTechnician(CRUDBase[Technician, TechnicianCreate, TechnicianUpdate]):
    def __init__(self):
        super().__init__(Technician)

    def get(self, db: Session, technician_id: int) -> Optional[Technician]:
        """Obtener técnico por ID"""
        return db.query(Technician).filter(Technician.technician_id == technician_id).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[Technician]:
        """Obtener técnico por email"""
        return db.query(Technician).filter(Technician.email == email).first()

    def get_by_specialization(self, db: Session, *, specialization: str) -> List[Technician]:
        """Obtener técnicos por especialización"""
        return db.query(Technician).filter(Technician.specialization == specialization).all()

    def search_by_name(self, db: Session, *, name: str) -> List[Technician]:
        """Buscar técnicos por nombre (búsqueda parcial)"""
        return db.query(Technician).filter(Technician.name.ilike(f"%{name}%")).all()

    def get_available_specializations(self, db: Session) -> List[str]:
        """Obtener lista de especializaciones disponibles"""
        specializations = db.query(Technician.specialization).distinct().all()
        return [spec[0] for spec in specializations if spec[0] is not None]

    def remove(self, db: Session, *, technician_id: int) -> Technician:
        """Eliminar técnico por ID"""
        obj = db.query(Technician).filter(Technician.technician_id == technician_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj 