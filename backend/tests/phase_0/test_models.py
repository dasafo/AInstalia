#backend/tests/phase_0/test_models.py
"""
Tests para Modelos SQLAlchemy - Fase 0
"""
import pytest
import logging
from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from backend.models.client_model import Client
from backend.models.product_model import Product
from backend.models.technician_model import Technician
from backend.models.equipment_model import InstalledEquipment
from backend.models.intervention_model import Intervention
from backend.models.contract_model import Contract
from backend.models.order_model import Order, OrderItem
from backend.models.warehouse_model import Warehouse
from backend.models.stock_model import Stock
from backend.models.knowledge_feedback_model import KnowledgeFeedback
from backend.models.chat_session_model import ChatSession
from backend.models.chat_message_model import ChatMessage
from datetime import datetime

logger = logging.getLogger("ainstalia.tests")

class TestModels:
    """Tests para validar la correcta creación de modelos SQLAlchemy"""
    
    def test_client_model_creation(self, db_session: Session, sample_client_data):
        """Test creación de modelo Client"""
        logger.info("Testing Client model creation")
        
        client = Client(**sample_client_data)
        db_session.add(client)
        db_session.commit()
        
        assert client.client_id is not None
        assert client.name == sample_client_data["name"]
        assert client.email == sample_client_data["email"]
        assert client.phone == sample_client_data["phone"]
        assert client.address == sample_client_data["address"]
        
        logger.info(f"Client created with ID: {client.client_id}")
    
    def test_product_model_creation(self, db_session: Session):
        """Test creación de modelo Product"""
        logger.info("Testing Product model creation")
        
        # Usar los campos correctos del modelo Product
        product_data = {
            "sku": "PROD001",
            "name": "Producto Test",
            "description": "Descripción del producto test",
            "price": Decimal('99.99'),  # Usar Decimal para precios
            "spec_json": {"color": "azul", "peso": "1kg"}
        }
        
        product = Product(**product_data)
        db_session.add(product)
        db_session.commit()
        
        assert product.sku == product_data["sku"]
        assert product.name == product_data["name"]
        assert product.description == product_data["description"]
        assert product.price == product_data["price"]
        assert product.spec_json == product_data["spec_json"]
        
        logger.info(f"Product created with SKU: {product.sku}")
        
    def test_technician_model_creation(self, db_session: Session):
        """Test creación de modelo Technician"""
        logger.info("Testing Technician model creation")
        
        technician_data = {
            "name": "Técnico Test",
            "email": "tecnico@test.com", 
            "phone": "987654321",
            "zone": "Zona Norte"
        }
        
        technician = Technician(**technician_data)
        db_session.add(technician)
        db_session.commit()
        
        assert technician.technician_id is not None
        assert technician.name == technician_data["name"]
        assert technician.email == technician_data["email"]
        assert technician.phone == technician_data["phone"]
        assert technician.zone == technician_data["zone"]
        
        logger.info(f"Technician created with ID: {technician.technician_id}")
    
    def test_warehouse_model_creation(self, db_session: Session):
        """Test creación de modelo Warehouse"""
        logger.info("Testing Warehouse model creation")
        
        # Usar los campos correctos del modelo Warehouse
        warehouse_data = {
            "name": "Almacén Test"
        }
        
        warehouse = Warehouse(**warehouse_data)
        db_session.add(warehouse)
        db_session.commit()
        
        assert warehouse.warehouse_id is not None
        assert warehouse.name == warehouse_data["name"]
        
        logger.info(f"Warehouse created with ID: {warehouse.warehouse_id}")
    
    def test_equipment_model_creation(self, db_session: Session):
        """Test creación de modelo Equipment con relaciones"""
        logger.info("Testing Equipment model creation with relationships")
        
        # Crear dependencias primero
        client = Client(
            name="Cliente Equipment",
            email="equipment@test.com",
            phone="123456789",
            address="Dirección Equipment"
        )
        db_session.add(client)
        
        product = Product(
            sku="EQUIP001",
            name="Producto Equipment",
            description="Producto para test de equipment",
            price=Decimal('150.0')
        )
        db_session.add(product)
        db_session.commit()
        
        # Crear equipment usando los campos correctos del SQL
        equipment = InstalledEquipment(
            client_id=client.client_id,
            sku=product.sku,
            install_date=date(2024, 1, 15),
            status="activo",
            config_json={"configuracion": "test"}
        )
        db_session.add(equipment)
        db_session.commit()
        
        assert equipment.equipment_id is not None
        assert equipment.client_id == client.client_id
        assert equipment.sku == product.sku
        assert equipment.status == "activo"
        
        logger.info(f"Equipment created with ID: {equipment.equipment_id}")
    
    def test_stock_model_creation(self, db_session: Session):
        """Test creación de modelo Stock con relaciones"""
        logger.info("Testing Stock model creation with relationships")
        
        # Crear dependencias primero
        product = Product(
            sku="STOCK001",
            name="Producto Stock",
            description="Producto para test de stock",
            price=Decimal('50.0')
        )
        db_session.add(product)
        
        warehouse = Warehouse(name="Almacén Stock")
        db_session.add(warehouse)
        db_session.commit()
        
        # Crear stock usando el campo correcto: sku (no product_sku)
        stock = Stock(
            sku=product.sku,
            warehouse_id=warehouse.warehouse_id,
            quantity=100
        )
        db_session.add(stock)
        db_session.commit()
        
        assert stock.stock_id is not None
        assert stock.sku == product.sku
        assert stock.warehouse_id == warehouse.warehouse_id
        assert stock.quantity == 100
        
        logger.info(f"Stock created with ID: {stock.stock_id}")
    
    def test_chat_models_creation(self, db_session: Session):
        """Test creación de modelos de Chat (Session y Message)"""
        logger.info("Testing Chat models creation")
        
        # Crear cliente primero
        client = Client(
            name="Cliente Chat",
            email="chat@test.com",
            phone="123456789",
            address="Dirección Chat"
        )
        db_session.add(client)
        db_session.commit()
        
        # Crear sesión de chat
        chat_session = ChatSession(
            chat_id="CHAT001",
            client_id=client.client_id,
            topic="Test Topic"
        )
        db_session.add(chat_session)
        db_session.commit()
        
        # Crear mensaje de chat - usar timestamp actual
        chat_message = ChatMessage(
            chat_id=chat_session.chat_id,
            message_timestamp=datetime.now(),
            sender="cliente",
            message_text="Hola, necesito ayuda"
        )
        db_session.add(chat_message)
        db_session.commit()
        
        assert chat_session.chat_id == "CHAT001"
        assert chat_session.client_id == client.client_id
        assert chat_session.topic == "Test Topic"
        
        assert chat_message.message_id is not None
        assert chat_message.chat_id == "CHAT001"
        assert chat_message.sender == "cliente"
        assert chat_message.message_text == "Hola, necesito ayuda"
        
        logger.info("Chat models created successfully")
    
    def test_knowledge_feedback_model_creation(self, db_session: Session):
        """Test creación de modelo KnowledgeFeedback"""
        logger.info("Testing KnowledgeFeedback model creation")
        
        # Usar los campos correctos del modelo KnowledgeFeedback
        feedback = KnowledgeFeedback(
            question="¿Cómo instalar el producto?",
            expected_answer="Siga los pasos del manual",
            user_type="cliente",
            status="pendiente"
        )
        db_session.add(feedback)
        db_session.commit()
        
        assert feedback.feedback_id is not None
        assert feedback.question == "¿Cómo instalar el producto?"
        assert feedback.expected_answer == "Siga los pasos del manual"
        assert feedback.user_type == "cliente"
        assert feedback.status == "pendiente"
        
        logger.info(f"KnowledgeFeedback created with ID: {feedback.feedback_id}")
    
    def test_all_models_table_creation(self, db_session: Session):
        """Test que todas las tablas de modelos se crean correctamente"""
        logger.info("Testing all model tables creation")
        
        # Usar inspector de SQLAlchemy para obtener tablas
        inspector = inspect(db_session.get_bind())
        table_names = inspector.get_table_names()
        
        expected_tables = [
            "clients", "products", "technicians", "installed_equipment",
            "interventions", "contracts", "orders", "order_items", 
            "warehouses", "stock", "knowledge_feedback", 
            "chat_sessions", "chat_messages"
        ]
        
        for table_name in expected_tables:
            assert table_name in table_names, f"Tabla {table_name} no encontrada"
        
        logger.info(f"All {len(expected_tables)} expected tables found: {expected_tables}") 