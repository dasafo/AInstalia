#backend/db/crud/equipment_crud.py
"""
Operaciones CRUD para Equipo Instalado
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from backend.models.equipment_model import InstalledEquipment
from backend.schemas.equipment_schema import InstalledEquipmentCreate, InstalledEquipmentUpdate
from backend.crud.base_crud import CRUDBase


class CRUDInstalledEquipment(CRUDBase[InstalledEquipment, InstalledEquipmentCreate, InstalledEquipmentUpdate]):
    def __init__(self):
        super().__init__(InstalledEquipment)

    def get(self, db: Session, equipment_id: int) -> Optional[InstalledEquipment]:
        """Obtener equipo por ID"""
        return db.query(InstalledEquipment).filter(InstalledEquipment.equipment_id == equipment_id).first()

    def get_by_client(self, db: Session, *, client_id: int) -> List[InstalledEquipment]:
        """Obtener equipos instalados de un cliente"""
        return db.query(InstalledEquipment).filter(InstalledEquipment.client_id == client_id).all()

    def get_by_sku(self, db: Session, *, sku: str) -> List[InstalledEquipment]:
        """Obtener equipos por SKU de producto"""
        return db.query(InstalledEquipment).filter(InstalledEquipment.sku == sku).all()

    def get_by_status(self, db: Session, *, status: str) -> List[InstalledEquipment]:
        """Obtener equipos por estado"""
        return db.query(InstalledEquipment).filter(InstalledEquipment.status == status).all()

    def get_by_date_range(
        self, db: Session, *, start_date: date, end_date: date
    ) -> List[InstalledEquipment]:
        """Obtener equipos instalados en rango de fechas"""
        return db.query(InstalledEquipment).filter(
            InstalledEquipment.installation_date >= start_date,
            InstalledEquipment.installation_date <= end_date
        ).all()

    def get_active_equipment(self, db: Session) -> List[InstalledEquipment]:
        """Obtener equipos activos"""
        return db.query(InstalledEquipment).filter(InstalledEquipment.status == "activo").all()

    def remove(self, db: Session, *, equipment_id: int) -> InstalledEquipment:
        """Eliminar equipo por ID"""
        obj = db.query(InstalledEquipment).filter(InstalledEquipment.equipment_id == equipment_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj 