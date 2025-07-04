#backend/tests/phase_0/test_crud.py
"""
Tests para Operaciones CRUD - Fase 0
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from datetime import datetime

from backend.crud import (
    client_crud, product_crud, warehouse_crud, stock_crud,
    chat_session_crud, chat_message_crud, knowledge_feedback_crud
)
from backend.schemas.client_schema import ClientCreate, ClientUpdate
from backend.schemas.product_schema import ProductCreate, ProductUpdate
from backend.schemas.warehouse_schema import WarehouseCreate, WarehouseUpdate
from backend.schemas.stock_schema import StockCreate, StockUpdate
from backend.schemas.chat_session_schema import ChatSessionCreate
from backend.schemas.chat_message_schema import ChatMessageCreate
from backend.schemas.knowledge_feedback_schema import KnowledgeFeedbackCreate

from backend.core.logging import get_logger

logger = get_logger("ainstalia.tests")

class TestCRUD:
    """Tests para todas las operaciones CRUD"""
    
    async def test_client_crud_operations(self, async_db_session: AsyncSession, sample_client_data):
        """Test operaciones CRUD completas para Client"""
        logger.info("Testing Client CRUD operations")
        
        # CREATE
        client_create = ClientCreate(**sample_client_data)
        created_client = await client_crud.create(async_db_session, obj_in=client_create)
        
        assert created_client.client_id is not None
        assert created_client.name == sample_client_data["name"]
        assert created_client.email == sample_client_data["email"]
        
        # READ
        fetched_client = await client_crud.get(async_db_session, client_id=created_client.client_id)
        assert fetched_client is not None
        assert fetched_client.client_id == created_client.client_id
        
        # READ by email
        client_by_email = await client_crud.get_by_email(async_db_session, email=sample_client_data["email"])
        assert client_by_email is not None
        assert client_by_email.email == sample_client_data["email"]
        
        # UPDATE
        update_data = ClientUpdate(name="Cliente Actualizado", phone="987654321")
        updated_client = await client_crud.update(async_db_session, db_obj=created_client, obj_in=update_data)
        
        assert updated_client.name == "Cliente Actualizado"
        assert updated_client.phone == "987654321"
        assert updated_client.email == sample_client_data["email"]  # No cambió
        
        # SEARCH
        search_results = await client_crud.search_by_name(async_db_session, name="Actualizado")
        assert len(search_results) > 0
        assert any(client.name == "Cliente Actualizado" for client in search_results)
        
        # DELETE
        deleted_client = await client_crud.remove(async_db_session, client_id=created_client.client_id)
        assert deleted_client.client_id == created_client.client_id
        
        # Verificar que se eliminó
        fetched_after_delete = await client_crud.get(async_db_session, client_id=created_client.client_id)
        assert fetched_after_delete is None
        
    async def test_product_crud_operations(self, async_db_session: AsyncSession):
        """Test operaciones CRUD para Product"""
        logger.info("Testing Product CRUD operations")
        
        # Crear producto con campos correctos
        product_data = {
            "sku": "CRUD001",
            "name": "Producto CRUD",
            "description": "Producto para test CRUD",
            "price": Decimal("75.50"),  # Usar Decimal
            "spec_json": {"color": "verde"}
        }
        
        # CREATE
        created_product = await product_crud.create(async_db_session, obj_in=ProductCreate(**product_data))
        assert created_product.sku == product_data["sku"]
        assert created_product.price == product_data["price"]
        
        # READ
        retrieved_product = await product_crud.get(async_db_session, sku=created_product.sku)
        assert retrieved_product is not None
        assert retrieved_product.name == product_data["name"]
        
        # UPDATE
        update_data = {"name": "Producto Actualizado", "price": Decimal("80.00")}
        updated_product = await product_crud.update(async_db_session, db_obj=created_product, obj_in=ProductUpdate(**update_data))
        assert updated_product.name == "Producto Actualizado"
        assert updated_product.price == Decimal("80.00")
        
        # DELETE
        deleted_product = await product_crud.remove(async_db_session, sku=created_product.sku)
        assert deleted_product is not None  # El método remove devuelve el objeto eliminado
        
        # Verificar que fue eliminado
        retrieved_product = await product_crud.get(async_db_session, sku=created_product.sku)
        assert retrieved_product is None
        
        logger.info("Product CRUD operations successful")
        
    async def test_warehouse_crud_operations(self, async_db_session: AsyncSession, sample_warehouse_data):
        """Test operaciones CRUD completas para Warehouse"""
        logger.info("Testing Warehouse CRUD operations")
        
        # CREATE
        warehouse_create = WarehouseCreate(**sample_warehouse_data)
        created_warehouse = await warehouse_crud.create(async_db_session, obj_in=warehouse_create)
        
        assert created_warehouse.warehouse_id is not None
        assert created_warehouse.name == sample_warehouse_data["name"]
        
        # READ by name
        warehouse_by_name = await warehouse_crud.get_by_name(async_db_session, name=sample_warehouse_data["name"])
        assert warehouse_by_name is not None
        assert warehouse_by_name.name == sample_warehouse_data["name"]
        
        # SEARCH
        search_results = await warehouse_crud.search_by_name(async_db_session, name="Test")
        assert len(search_results) > 0
        
    async def test_stock_crud_operations(self, async_db_session: AsyncSession):
        """Test operaciones CRUD para Stock con relaciones"""
        logger.info("Testing Stock CRUD operations with relationships")
        
        # Crear dependencias
        from backend.schemas.product_schema import ProductCreate
        from backend.schemas.warehouse_schema import WarehouseCreate
        
        product_data = ProductCreate(
            sku="STOCK_TEST",
            name="Producto Stock Test",
            description="Producto para test de stock",
            price=75.0,
            category="Test"
        )
        warehouse_data = WarehouseCreate(
            name="Almacén Stock Test",
            location="Ubicación Test",
            capacity=1000
        )
        
        created_product = await product_crud.create(async_db_session, obj_in=product_data)
        created_warehouse = await warehouse_crud.create(async_db_session, obj_in=warehouse_data)
        
        # CREATE Stock
        stock_data = StockCreate(
            sku=created_product.sku,
            warehouse_id=created_warehouse.warehouse_id,
            quantity=50,
            min_stock=10,
            max_stock=100
        )
        
        created_stock = await stock_crud.create(async_db_session, obj_in=stock_data)
        assert created_stock.stock_id is not None
        assert created_stock.quantity == 50
        
        # READ by SKU and Warehouse
        stock_by_sku_warehouse = await stock_crud.get_by_sku_and_warehouse(
            async_db_session, 
            sku=created_product.sku, 
            warehouse_id=created_warehouse.warehouse_id
        )
        assert stock_by_sku_warehouse is not None
        assert stock_by_sku_warehouse.quantity == 50
        
        # GET by SKU (all warehouses)
        stock_by_sku = await stock_crud.get_by_sku(async_db_session, sku=created_product.sku)
        assert len(stock_by_sku) > 0
        
        # LOW STOCK test
        # Actualizar a cantidad baja
        low_stock_update = StockUpdate(quantity=3)
        updated_stock = await stock_crud.update(async_db_session, db_obj=created_stock, obj_in=low_stock_update)
        
        low_stock_items = await stock_crud.get_low_stock(async_db_session, min_quantity=5)
        assert len(low_stock_items) > 0
        assert any(item.stock_id == updated_stock.stock_id for item in low_stock_items)
        
    async def test_chat_crud_operations(self, async_db_session: AsyncSession):
        """Test operaciones CRUD para Chat Session y Message"""
        logger.info("Testing Chat CRUD operations")
        
        # Crear cliente primero
        client_data = {
            "name": "Cliente Chat CRUD",
            "email": "chatcrud@test.com",
            "phone": "987654321",
            "address": "Dirección Chat CRUD"
        }
        client = await client_crud.create(async_db_session, obj_in=ClientCreate(**client_data))
        
        # Crear sesión de chat
        chat_session_data = {
            "chat_id": "CHATCRUD001",
            "client_id": client.client_id,
            "topic": "Test CRUD"
        }
        chat_session = await chat_session_crud.create(async_db_session, obj_in=ChatSessionCreate(**chat_session_data))
        assert chat_session.chat_id == "CHATCRUD001"
        
        # Para el mensaje de chat, crear sin timestamp (que se auto-asigna)
        chat_message_data = {
            "chat_id": chat_session.chat_id,
            "sender": "cliente",
            "message_text": "Mensaje de prueba CRUD"
        }
        chat_message = await chat_message_crud.create(async_db_session, obj_in=ChatMessageCreate(**chat_message_data))
        assert chat_message.sender == "cliente"
        assert chat_message.message_text == "Mensaje de prueba CRUD"
        assert chat_message.message_timestamp is not None  # Se auto-asigna
        
        logger.info("Chat CRUD operations successful")
        
    async def test_knowledge_feedback_crud_operations(self, async_db_session: AsyncSession):
        """Test operaciones CRUD para Knowledge Feedback"""
        logger.info("Testing Knowledge Feedback CRUD operations")
        
        # CREATE
        feedback_data = KnowledgeFeedbackCreate(
            user_type="cliente",
            question="¿Cómo configurar el producto X?",
            expected_answer="Debe seguir estos pasos...",
            actual_answer="No sé cómo hacerlo",
            status="pendiente"
        )
        
        created_feedback = await knowledge_feedback_crud.create(async_db_session, obj_in=feedback_data)
        assert created_feedback.feedback_id is not None
        assert created_feedback.user_type == "cliente"
        assert created_feedback.status == "pendiente"
        
        # GET by status
        pending_feedback = await knowledge_feedback_crud.get_pending_feedback(async_db_session)
        assert len(pending_feedback) > 0
        assert any(fb.feedback_id == created_feedback.feedback_id for fb in pending_feedback)
        
        # SEARCH by question
        search_results = await knowledge_feedback_crud.search_by_question(async_db_session, question="configurar")
        assert len(search_results) > 0
        
    @pytest.mark.asyncio
    async def test_crud_pagination(self, async_db_session: AsyncSession):
        """Test paginación genérica de CRUD"""
        logger.info("Testing generic CRUD pagination")
        
        # Crear 5 clientes de ejemplo
        clients_data = [
            ClientCreate(name=f"Cliente {i}", email=f"cliente{i}@test.com", phone=f"11111111{i}", address=f"Dirección {i}")
            for i in range(1, 6)
        ]
        
        for client_data in clients_data:
            await client_crud.create(async_db_session, obj_in=client_data)

        # Obtener los primeros 3 clientes
        clients_page1 = await client_crud.get_multi(async_db_session, skip=0, limit=3)
        assert len(clients_page1) == 3
        assert clients_page1[0].name == "Cliente 1"
        assert clients_page1[2].name == "Cliente 3"

        # Obtener los siguientes 2 clientes
        clients_page2 = await client_crud.get_multi(async_db_session, skip=3, limit=3)
        assert len(clients_page2) == 2
        assert clients_page2[0].name == "Cliente 4"
        assert clients_page2[1].name == "Cliente 5"

        # Obtener todos los clientes (sin límite)
        all_clients = await client_crud.get_multi(async_db_session)
        assert len(all_clients) == 5

        logger.info("CRUD pagination test successful")
    
    @pytest.mark.asyncio
    async def test_crud_error_handling(self, async_db_session: AsyncSession):
        """Test manejo de errores en operaciones CRUD"""
        logger.info("Testing CRUD error handling")
        
        # Intentar obtener un cliente que no existe
        non_existent_client = await client_crud.get(async_db_session, client_id=99999)
        assert non_existent_client is None
        
        # Intentar eliminar un cliente que no existe
        deleted_non_existent = await client_crud.remove(async_db_session, client_id=99999)
        assert deleted_non_existent is None
        
        logger.info("CRUD error handling test successful")