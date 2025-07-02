# Esquemas Pydantic

# Esquemas existentes
from .client_schema import (
    ClientBase, ClientCreate, ClientUpdate, ClientResponse, ClientWithRelations
)
from .product_schema import (
    ProductBase, ProductCreate, ProductUpdate, ProductResponse, ProductWithRelations
)
from .technician_schema import (
    TechnicianBase, TechnicianCreate, TechnicianUpdate, TechnicianResponse, TechnicianWithRelations
)
from .equipment_schema import (
    InstalledEquipmentBase, InstalledEquipmentCreate, InstalledEquipmentUpdate, 
    InstalledEquipmentResponse, InstalledEquipmentWithRelations
)
from .intervention_schema import (
    InterventionBase, InterventionCreate, InterventionUpdate, InterventionResponse, InterventionWithRelations
)
from .contract_schema import (
    ContractBase, ContractCreate, ContractUpdate, ContractResponse, ContractWithRelations
)
from .order_schema import (
    OrderBase, OrderCreate, OrderUpdate, OrderResponse, OrderWithItems,
    OrderItemBase, OrderItemCreate, OrderItemUpdate, OrderItemResponse, OrderItemWithRelations
)

# Esquemas nuevos
from .warehouse_schema import (
    WarehouseBase, WarehouseCreate, WarehouseUpdate, WarehouseResponse, WarehouseWithRelations
)
from .stock_schema import (
    StockBase, StockCreate, StockUpdate, StockResponse, StockWithRelations
)
from .knowledge_feedback_schema import (
    KnowledgeFeedbackBase, KnowledgeFeedbackCreate, KnowledgeFeedbackUpdate, KnowledgeFeedbackResponse
)
from .chat_session_schema import (
    ChatSessionBase, ChatSessionCreate, ChatSessionUpdate, ChatSessionResponse, ChatSessionWithRelations
)
from .chat_message_schema import (
    ChatMessageBase, ChatMessageCreate, ChatMessageUpdate, ChatMessageResponse, ChatMessageWithRelations
)

# AI Schemas
from .ai_schema import (
    UserRole, SQLQueryRequest, SQLQueryResponse, BusinessInsightsResponse,
    KnowledgeQueryRequest, KnowledgeQueryResponse, FeedbackRequest,
    FeedbackResponse, AIHealthResponse, QueryStats, AIUsageStats
)

__all__ = [
    # Client schemas
    "ClientBase", "ClientCreate", "ClientUpdate", "ClientResponse", "ClientWithRelations",
    # Product schemas
    "ProductBase", "ProductCreate", "ProductUpdate", "ProductResponse", "ProductWithRelations",
    # Technician schemas
    "TechnicianBase", "TechnicianCreate", "TechnicianUpdate", "TechnicianResponse", "TechnicianWithRelations",
    # Equipment schemas
    "InstalledEquipmentBase", "InstalledEquipmentCreate", "InstalledEquipmentUpdate", 
    "InstalledEquipmentResponse", "InstalledEquipmentWithRelations",
    # Intervention schemas
    "InterventionBase", "InterventionCreate", "InterventionUpdate", "InterventionResponse", "InterventionWithRelations",
    # Contract schemas
    "ContractBase", "ContractCreate", "ContractUpdate", "ContractResponse", "ContractWithRelations",
    # Order schemas
    "OrderBase", "OrderCreate", "OrderUpdate", "OrderResponse", "OrderWithItems",
    "OrderItemBase", "OrderItemCreate", "OrderItemUpdate", "OrderItemResponse", "OrderItemWithRelations",
    # Warehouse schemas
    "WarehouseBase", "WarehouseCreate", "WarehouseUpdate", "WarehouseResponse", "WarehouseWithRelations",
    # Stock schemas
    "StockBase", "StockCreate", "StockUpdate", "StockResponse", "StockWithRelations",
    # Knowledge Feedback schemas
    "KnowledgeFeedbackBase", "KnowledgeFeedbackCreate", "KnowledgeFeedbackUpdate", "KnowledgeFeedbackResponse",
    # Chat Session schemas
    "ChatSessionBase", "ChatSessionCreate", "ChatSessionUpdate", "ChatSessionResponse", "ChatSessionWithRelations",
    # Chat Message schemas
    "ChatMessageBase", "ChatMessageCreate", "ChatMessageUpdate", "ChatMessageResponse", "ChatMessageWithRelations",
    # AI schemas
    "UserRole", "SQLQueryRequest", "SQLQueryResponse", "BusinessInsightsResponse",
    "KnowledgeQueryRequest", "KnowledgeQueryResponse", "FeedbackRequest",
    "FeedbackResponse", "AIHealthResponse", "QueryStats", "AIUsageStats",
]

# Schemas package