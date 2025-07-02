#backend/tests/phase_0/test_schemas.py
"""
Tests para Esquemas Pydantic - Fase 0
"""
import pytest
from pydantic import ValidationError
from decimal import Decimal
from datetime import datetime

from backend.schemas.client_schema import ClientCreate, ClientUpdate, ClientResponse
from backend.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from backend.schemas.warehouse_schema import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from backend.schemas.stock_schema import StockCreate, StockUpdate, StockResponse
from backend.schemas.chat_session_schema import ChatSessionCreate, ChatSessionUpdate, ChatSessionResponse
from backend.schemas.chat_message_schema import ChatMessageCreate, ChatMessageUpdate, ChatMessageResponse
from backend.schemas.knowledge_feedback_schema import KnowledgeFeedbackCreate, KnowledgeFeedbackUpdate

from backend.core.logging import get_logger
from backend.schemas import (
    client_schema, product_schema, warehouse_schema, stock_schema,
    chat_session_schema, chat_message_schema, knowledge_feedback_schema,
    equipment_schema, intervention_schema, contract_schema, order_schema
)

logger = get_logger("ainstalia.tests")

class TestSchemas:
    """Tests para todos los esquemas Pydantic"""
    
    def test_client_schema_validation(self):
        """Test validación del schema Client"""
        logger.info("Testing Client schema validation")
        
        # Test con datos válidos (campos del SQL)
        valid_data = {
            "name": "Cliente Test",
            "email": "test@client.com",
            "phone": "123456789",
            "address": "Dirección Test"
        }
        client = ClientCreate(**valid_data)
        
        assert client.name == valid_data["name"]
        assert client.email == valid_data["email"]
        assert client.phone == valid_data["phone"]
        assert client.address == valid_data["address"]
        
        logger.info("Client schema validation successful")

    def test_product_schema_validation(self):
        """Test validación del schema Product"""
        logger.info("Testing Product schema validation")
        
        # Test con datos válidos
        valid_data = {
            "sku": "PROD001",
            "name": "Producto Test",
            "description": "Descripción del producto",
            "price": Decimal("99.99"),  # Usar Decimal
            "spec_json": {"color": "azul", "peso": "1kg"}
        }
        product = ProductCreate(**valid_data)
        
        assert product.sku == valid_data["sku"]
        assert product.name == valid_data["name"]
        assert product.description == valid_data["description"]
        assert product.price == valid_data["price"]
        assert product.spec_json == valid_data["spec_json"]
        
        logger.info("Product schema validation successful")

    def test_warehouse_schema_validation(self):
        """Test validación del schema Warehouse"""
        logger.info("Testing Warehouse schema validation")
        
        # Test con datos válidos (solo name según SQL)
        valid_data = {
            "name": "Almacén Test"
        }
        warehouse = WarehouseCreate(**valid_data)
        
        assert warehouse.name == valid_data["name"]
        
        logger.info("Warehouse schema validation successful")

    def test_stock_schema_validation(self):
        """Test validación del schema Stock"""
        logger.info("Testing Stock schema validation")
        
        # Test con datos válidos
        valid_data = {
            "sku": "PROD001",
            "warehouse_id": 1,
            "quantity": 100
        }
        stock = StockCreate(**valid_data)
        
        assert stock.sku == valid_data["sku"]
        assert stock.warehouse_id == valid_data["warehouse_id"]
        assert stock.quantity == valid_data["quantity"]
        
        logger.info("Stock schema validation successful")

    def test_chat_message_schema_validation(self):
        """Test validación del schema ChatMessage"""
        logger.info("Testing ChatMessage schema validation")
        
        # Test con datos válidos incluyendo message_timestamp
        valid_data = {
            "chat_id": "CHAT001",
            "message_timestamp": datetime.now(),
            "sender": "cliente",
            "message_text": "Mensaje de prueba"
        }
        chat_message = ChatMessageCreate(**valid_data)
        
        assert chat_message.chat_id == valid_data["chat_id"]
        assert chat_message.message_timestamp == valid_data["message_timestamp"]
        assert chat_message.sender == valid_data["sender"]
        assert chat_message.message_text == valid_data["message_text"]
        
        logger.info("ChatMessage schema validation successful")

    def test_knowledge_feedback_schema_validation(self):
        """Test validación del schema KnowledgeFeedback"""
        logger.info("Testing KnowledgeFeedback schema validation")
        
        # Test con datos válidos
        valid_data = {
            "question": "¿Cómo configurar el producto?",
            "expected_answer": "Siga las instrucciones del manual",
            "user_type": "cliente",
            "status": "pendiente"
        }
        feedback = KnowledgeFeedbackCreate(**valid_data)
        
        assert feedback.question == valid_data["question"]
        assert feedback.expected_answer == valid_data["expected_answer"]
        assert feedback.user_type == valid_data["user_type"]
        assert feedback.status == valid_data["status"]
        
        # Test con user_type inválido
        invalid_data = valid_data.copy()
        invalid_data["user_type"] = "tipo_invalido"
        
        with pytest.raises(ValidationError):
            KnowledgeFeedbackCreate(**invalid_data)
        
        logger.info("KnowledgeFeedback schema validation successful")

    def test_all_schema_types_exist(self):
        """Test que todos los tipos de schema existen"""
        logger.info("Testing all schema types exist")
        
        # Lista de schemas básicos que deben existir
        schema_checks = [
            (client_schema, 'ClientCreate'),
            (product_schema, 'ProductCreate'),
            (warehouse_schema, 'WarehouseCreate'),
            (stock_schema, 'StockCreate'),
            (chat_session_schema, 'ChatSessionCreate'),
            (chat_message_schema, 'ChatMessageCreate'),
            (knowledge_feedback_schema, 'KnowledgeFeedbackCreate'),
            (equipment_schema, 'InstalledEquipmentCreate'),
            (intervention_schema, 'InterventionCreate'),
            (contract_schema, 'ContractCreate'),
            (order_schema, 'OrderCreate'),
        ]
        
        for module, class_name in schema_checks:
            assert hasattr(module, class_name), f"{class_name} not found in {module.__name__}"
        
        logger.info("All schema types validation successful") 