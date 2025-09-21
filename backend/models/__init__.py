# Modelos SQLAlchemy

from .client_model import Client
from .product_model import Product
from .technician_model import Technician
from .equipment_model import InstalledEquipment
from .intervention_model import Intervention
from .contract_model import Contract
from .order_model import Order, OrderItem
from .warehouse_model import Warehouse
from .stock_model import Stock
from .knowledge_feedback_model import KnowledgeFeedback
from .chat_session_model import ChatSession
from .chat_message_model import ChatMessage

__all__ = [
    # Modelos existentes
    "Client",
    "Product", 
    "Technician",
    "InstalledEquipment",
    "Intervention",
    "Contract",
    "Order",
    "OrderItem",
    "Warehouse",
    "Stock",
    "KnowledgeFeedback",
    "ChatSession",
    "ChatMessage",
]

# Models package