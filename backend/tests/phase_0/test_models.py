#backend/tests/phase_0/test_models.py
"""
Tests para Modelos SQLAlchemy - Fase 0
"""
import pytest
import logging
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
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
from sqlalchemy.orm import declarative_base

logger = logging.getLogger("ainstalia.tests")

class TestModels:
    """Tests para validar la correcta creación de modelos SQLAlchemy"""
    
    async def test_client_model_creation(self, async_db_session: AsyncSession, sample_client_data):
        """Test creación de modelo Client"""
        logger.info("Testing Client model creation")
        
        client = Client(**sample_client_data)
        async_db_session.add(client)
        await async_db_session.commit()
        await async_db_session.refresh(client)
        
        assert client.client_id is not None
        assert client.name == sample_client_data["name"]
        assert client.email == sample_client_data["email"]
        assert client.phone == sample_client_data["phone"]
        assert client.address == sample_client_data["address"]
        
        logger.info(f"Client created with ID: {client.client_id}")
    
    async def test_product_model_creation(self, async_db_session: AsyncSession):
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
        async_db_session.add(product)
        await async_db_session.commit()
        await async_db_session.refresh(product)
        
        assert product.sku == product_data["sku"]
        assert product.name == product_data["name"]
        assert product.description == product_data["description"]
        assert product.price == product_data["price"]
        assert product.spec_json == product_data["spec_json"]
        
        logger.info(f"Product created with SKU: {product.sku}")
        
    async def test_technician_model_creation(self, async_db_session: AsyncSession):
        """Test creación de modelo Technician"""
        logger.info("Testing Technician model creation")
        
        technician_data = {
            "name": "Técnico Test",
            "email": "tecnico@test.com", 
            "phone": "987654321",
            "zone": "Zona Norte"
        }
        
        technician = Technician(**technician_data)
        async_db_session.add(technician)
        await async_db_session.commit()
        await async_db_session.refresh(technician)
        
        assert technician.technician_id is not None
        assert technician.name == technician_data["name"]
        assert technician.email == technician_data["email"]
        assert technician.phone == technician_data["phone"]
        assert technician.zone == technician_data["zone"]
        
        logger.info(f"Technician created with ID: {technician.technician_id}")
    
    async def test_warehouse_model_creation(self, async_db_session: AsyncSession):
        """Test creación de modelo Warehouse"""
        logger.info("Testing Warehouse model creation")
        
        # Usar los campos correctos del modelo Warehouse
        warehouse_data = {
            "name": "Almacén Test"
        }
        
        warehouse = Warehouse(**warehouse_data)
        async_db_session.add(warehouse)
        await async_db_session.commit()
        await async_db_session.refresh(warehouse)
        
        assert warehouse.warehouse_id is not None
        assert warehouse.name == warehouse_data["name"]
        
        logger.info(f"Warehouse created with ID: {warehouse.warehouse_id}")
    
    async def test_equipment_model_creation(self, async_db_session: AsyncSession):
        """Test creación de modelo Equipment con relaciones"""
        logger.info("Testing Equipment model creation with relationships")
        
        # Crear dependencias primero
        client = Client(
            name="Cliente Equipment",
            email="equipment@test.com",
            phone="123456789",
            address="Dirección Equipment"
        )
        async_db_session.add(client)
        
        product = Product(
            sku="EQUIP001",
            name="Producto Equipment",
            description="Producto para test de equipment",
            price=Decimal('150.0')
        )
        async_db_session.add(product)
        await async_db_session.commit()
        await async_db_session.refresh(client)
        await async_db_session.refresh(product)
        
        # Crear equipment usando los campos correctos del SQL
        equipment = InstalledEquipment(
            client_id=client.client_id,
            sku=product.sku,
            install_date=date(2024, 1, 15),
            status="activo",
            config_json={"configuracion": "test"}
        )
        async_db_session.add(equipment)
        await async_db_session.commit()
        await async_db_session.refresh(equipment)
        
        assert equipment.equipment_id is not None
        assert equipment.client_id == client.client_id
        assert equipment.sku == product.sku
        assert equipment.status == "activo"
        
        logger.info(f"Equipment created with ID: {equipment.equipment_id}")
    
    async def test_stock_model_creation(self, async_db_session: AsyncSession):
        """Test creación de modelo Stock con relaciones"""
        logger.info("Testing Stock model creation with relationships")
        
        # Crear dependencias primero
        product = Product(
            sku="STOCK001",
            name="Producto Stock",
            description="Producto para test de stock",
            price=Decimal('50.0')
        )
        async_db_session.add(product)
        
        warehouse = Warehouse(name="Almacén Stock")
        async_db_session.add(warehouse)
        await async_db_session.commit()
        await async_db_session.refresh(product)
        await async_db_session.refresh(warehouse)
        
        # Crear stock usando el campo correcto: sku (no product_sku)
        stock = Stock(
            sku=product.sku,
            warehouse_id=warehouse.warehouse_id,
            quantity=100
        )
        async_db_session.add(stock)
        await async_db_session.commit()
        await async_db_session.refresh(stock)
        
        assert stock.stock_id is not None
        assert stock.sku == product.sku
        assert stock.warehouse_id == warehouse.warehouse_id
        assert stock.quantity == 100
        
        logger.info(f"Stock created with ID: {stock.stock_id}")
    
    async def test_chat_models_creation(self, async_db_session: AsyncSession):
        """Test creación de modelos de Chat (Session y Message)"""
        logger.info("Testing Chat models creation")
        
        # Crear cliente primero
        client = Client(
            name="Cliente Chat",
            email="chat@test.com",
            phone="123456789",
            address="Dirección Chat"
        )
        async_db_session.add(client)
        await async_db_session.commit()
        await async_db_session.refresh(client)
        
        # Crear sesión de chat
        chat_session = ChatSession(
            chat_id="CHAT001",
            client_id=client.client_id,
            topic="Test Topic"
        )
        async_db_session.add(chat_session)
        await async_db_session.commit()
        await async_db_session.refresh(chat_session)
        
        # Crear mensaje de chat - usar timestamp actual
        chat_message = ChatMessage(
            chat_id=chat_session.chat_id,
            message_timestamp=datetime.now(),
            sender="cliente",
            message_text="Hola, necesito ayuda"
        )
        async_db_session.add(chat_message)
        await async_db_session.commit()
        await async_db_session.refresh(chat_message)
        
        assert chat_session.chat_id == "CHAT001"
        assert chat_session.client_id == client.client_id
        assert chat_session.topic == "Test Topic"
        
        assert chat_message.message_id is not None
        assert chat_message.chat_id == "CHAT001"
        assert chat_message.sender == "cliente"
        assert chat_message.message_text == "Hola, necesito ayuda"
        
        logger.info("Chat models created successfully")
    
    async def test_knowledge_feedback_model_creation(self, async_db_session: AsyncSession):
        """Test creación de modelo KnowledgeFeedback"""
        logger.info("Testing KnowledgeFeedback model creation")
        
        # Usar los campos correctos del modelo KnowledgeFeedback
        feedback = KnowledgeFeedback(
            question="¿Cómo instalar el producto?",
            expected_answer="Siga los pasos del manual",
            user_type="cliente",
            status="pendiente"
        )
        async_db_session.add(feedback)
        await async_db_session.commit()
        await async_db_session.refresh(feedback)
        
        assert feedback.feedback_id is not None
        assert feedback.question == "¿Cómo instalar el producto?"
        assert feedback.expected_answer == "Siga los pasos del manual"
        assert feedback.user_type == "cliente"
        assert feedback.status == "pendiente"
        
        logger.info(f"KnowledgeFeedback created with ID: {feedback.feedback_id}")
    
    async def test_all_models_table_creation(self, async_db_session: AsyncSession):
        """Test para verificar que todas las tablas de los modelos se crean en la BD"""
        logger.info("Testing if all model tables are created in the database")

        inspector = inspect(async_db_session.bind)
        existing_tables = await inspector.get_table_names()

        # Obtener los nombres de las tablas declaradas en Base.metadata
        declared_tables = [table.name for table in declarative_base().metadata.sorted_tables]
        
        # Verificar que todas las tablas declaradas existen en la base de datos
        for table_name in declared_tables:
            assert table_name in existing_tables, f"Table {table_name} was not created in the database."

        logger.info("All model tables confirmed to be created successfully.") 