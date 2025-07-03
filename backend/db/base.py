#backend/db/base.py
"""
Base para modelos SQLAlchemy
"""
from sqlalchemy.orm import declarative_base

# Base class para todos los modelos
Base = declarative_base()

# Importar todos los modelos para que Alembic los detecte
from backend.models.client_model import Client  # noqa
from backend.models.equipment_model import InstalledEquipment  # noqa
from backend.models.product_model import Product  # noqa
from backend.models.technician_model import Technician  # noqa
from backend.models.order_model import Order  # noqa
from backend.models.intervention_model import Intervention  # noqa
from backend.models.stock_model import Stock  # noqa
from backend.models.warehouse_model import Warehouse  # noqa
from backend.models.contract_model import Contract  # noqa
from backend.models.chat_session_model import ChatSession  # noqa
from backend.models.chat_message_model import ChatMessage  # noqa
from backend.models.knowledge_feedback_model import KnowledgeFeedback  # noqa

# NOTA: Las importaciones de modelos están aquí para que Alembic
# pueda detectarlos y generar migraciones automáticamente.