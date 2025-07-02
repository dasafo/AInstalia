# Operaciones CRUD

# CRUD existentes
from .client_crud import CRUDClient
from .product_crud import CRUDProduct
from .technician_crud import CRUDTechnician
from .equipment_crud import CRUDInstalledEquipment
from .intervention_crud import CRUDIntervention
from .contract_crud import CRUDContract
from .order_crud import CRUDOrder, CRUDOrderItem

# CRUD nuevos
from .warehouse_crud import CRUDWarehouse
from .stock_crud import CRUDStock
from .knowledge_feedback_crud import CRUDKnowledgeFeedback
from .chat_session_crud import CRUDChatSession
from .chat_message_crud import CRUDChatMessage

# Instancias de CRUD
client_crud = CRUDClient()
product_crud = CRUDProduct()
technician_crud = CRUDTechnician()
equipment_crud = CRUDInstalledEquipment()
intervention_crud = CRUDIntervention()
contract_crud = CRUDContract()
order_crud = CRUDOrder()
order_item_crud = CRUDOrderItem()
warehouse_crud = CRUDWarehouse()
stock_crud = CRUDStock()
knowledge_feedback_crud = CRUDKnowledgeFeedback()
chat_session_crud = CRUDChatSession()
chat_message_crud = CRUDChatMessage()

__all__ = [
    # Clases CRUD
    "CRUDClient", "CRUDProduct", "CRUDTechnician", "CRUDInstalledEquipment",
    "CRUDIntervention", "CRUDContract", "CRUDOrder", "CRUDOrderItem",
    "CRUDWarehouse", "CRUDStock", "CRUDKnowledgeFeedback", 
    "CRUDChatSession", "CRUDChatMessage",
    # Instancias CRUD
    "client_crud", "product_crud", "technician_crud", "equipment_crud",
    "intervention_crud", "contract_crud", "order_crud", "order_item_crud",
    "warehouse_crud", "stock_crud", "knowledge_feedback_crud",
    "chat_session_crud", "chat_message_crud",
] 