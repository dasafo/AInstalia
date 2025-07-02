#backend/db/crud/intervention_crud.py
"""
Operaciones CRUD para Intervención
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from backend.db.models.intervention_model import Intervention
from backend.db.schemas.intervention_schema import InterventionCreate, InterventionUpdate
from backend.db.crud.base_crud import CRUDBase


class CRUDIntervention(CRUDBase[Intervention, InterventionCreate, InterventionUpdate]):
    def __init__(self):
        super().__init__(Intervention)

    def get(self, db: Session, intervention_id: int) -> Optional[Intervention]:
        """Obtener intervención por ID"""
        return db.query(Intervention).filter(Intervention.intervention_id == intervention_id).first()

    def get_by_client(self, db: Session, *, client_id: int) -> List[Intervention]:
        """Obtener intervenciones de un cliente"""
        return db.query(Intervention).filter(Intervention.client_id == client_id).all()

    def get_by_technician(self, db: Session, *, technician_id: int) -> List[Intervention]:
        """Obtener intervenciones de un técnico"""
        return db.query(Intervention).filter(Intervention.technician_id == technician_id).all()

    def get_by_equipment(self, db: Session, *, equipment_id: int) -> List[Intervention]:
        """Obtener intervenciones de un equipo"""
        return db.query(Intervention).filter(Intervention.equipment_id == equipment_id).all()

    def get_by_status(self, db: Session, *, status: str) -> List[Intervention]:
        """Obtener intervenciones por estado"""
        return db.query(Intervention).filter(Intervention.status == status).all()

    def get_by_date_range(
        self, db: Session, *, start_date: date, end_date: date
    ) -> List[Intervention]:
        """Obtener intervenciones en rango de fechas"""
        return db.query(Intervention).filter(
            Intervention.intervention_date >= start_date,
            Intervention.intervention_date <= end_date
        ).all()

    def get_pending_interventions(self, db: Session) -> List[Intervention]:
        """Obtener intervenciones pendientes"""
        return db.query(Intervention).filter(Intervention.status == "pendiente").all()

    def remove(self, db: Session, *, intervention_id: int) -> Intervention:
        """Eliminar intervención por ID"""
        obj = db.query(Intervention).filter(Intervention.intervention_id == intervention_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj 