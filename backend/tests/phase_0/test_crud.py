#backend/tests/phase_0/test_crud.py
"""
Tests para Operaciones CRUD - Fase 0
"""
import pytest
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime

from backend.db.crud import (
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
    
    def test_client_crud_operations(self, db_session: Session, sample_client_data):
        """Test operaciones CRUD completas para Client"""
        logger.info("Testing Client CRUD operations")
        
        # CREATE
        client_create = ClientCreate(**sample_client_data)
        created_client = client_crud.create(db_session, obj_in=client_create)
        
        assert created_client.client_id is not None
        assert created_client.name == sample_client_data["name"]
        assert created_client.email == sample_client_data["email"]
        
        # READ
        fetched_client = client_crud.get(db_session, client_id=created_client.client_id)
        assert fetched_client is not None
        assert fetched_client.client_id == created_client.client_id
        
        # READ by email
        client_by_email = client_crud.get_by_email(db_session, email=sample_client_data["email"])
        assert client_by_email is not None
        assert client_by_email.email == sample_client_data["email"]
        
        # UPDATE
        update_data = ClientUpdate(name="Cliente Actualizado", phone="987654321")
        updated_client = client_crud.update(db_session, db_obj=created_client, obj_in=update_data)
        
        assert updated_client.name == "Cliente Actualizado"
        assert updated_client.phone == "987654321"
        assert updated_client.email == sample_client_data["email"]  # No cambió
        
        # SEARCH
        search_results = client_crud.search_by_name(db_session, name="Actualizado")
        assert len(search_results) > 0
        assert any(client.name == "Cliente Actualizado" for client in search_results)
        
        # DELETE
        deleted_client = client_crud.remove(db_session, client_id=created_client.client_id)
        assert deleted_client.client_id == created_client.client_id
        
        # Verificar que se eliminó
        fetched_after_delete = client_crud.get(db_session, client_id=created_client.client_id)
        assert fetched_after_delete is None
        
    def test_product_crud_operations(self, db_session: Session):
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
        created_product = product_crud.create(db_session, obj_in=ProductCreate(**product_data))
        assert created_product.sku == product_data["sku"]
        assert created_product.price == product_data["price"]
        
        # READ
        retrieved_product = product_crud.get(db_session, sku=created_product.sku)
        assert retrieved_product is not None
        assert retrieved_product.name == product_data["name"]
        
        # UPDATE
        update_data = {"name": "Producto Actualizado", "price": Decimal("80.00")}
        updated_product = product_crud.update(db_session, db_obj=created_product, obj_in=ProductUpdate(**update_data))
        assert updated_product.name == "Producto Actualizado"
        assert updated_product.price == Decimal("80.00")
        
        # DELETE
        deleted_product = product_crud.remove(db_session, sku=created_product.sku)
        assert deleted_product is not None  # El método remove devuelve el objeto eliminado
        
        # Verificar que fue eliminado
        retrieved_product = product_crud.get(db_session, sku=created_product.sku)
        assert retrieved_product is None
        
        logger.info("Product CRUD operations successful")
        
    def test_warehouse_crud_operations(self, db_session: Session, sample_warehouse_data):
        """Test operaciones CRUD completas para Warehouse"""
        logger.info("Testing Warehouse CRUD operations")
        
        # CREATE
        warehouse_create = WarehouseCreate(**sample_warehouse_data)
        created_warehouse = warehouse_crud.create(db_session, obj_in=warehouse_create)
        
        assert created_warehouse.warehouse_id is not None
        assert created_warehouse.name == sample_warehouse_data["name"]
        
        # READ by name
        warehouse_by_name = warehouse_crud.get_by_name(db_session, name=sample_warehouse_data["name"])
        assert warehouse_by_name is not None
        assert warehouse_by_name.name == sample_warehouse_data["name"]
        
        # SEARCH
        search_results = warehouse_crud.search_by_name(db_session, name="Test")
        assert len(search_results) > 0
        
    def test_stock_crud_operations(self, db_session: Session):
        """Test operaciones CRUD para Stock con relaciones"""
        logger.info("Testing Stock CRUD operations with relationships")
        
        # Crear dependencias
        from backend.db.schemas.product_schema import ProductCreate
        from backend.db.schemas.warehouse_schema import WarehouseCreate
        
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
        
        created_product = product_crud.create(db_session, obj_in=product_data)
        created_warehouse = warehouse_crud.create(db_session, obj_in=warehouse_data)
        
        # CREATE Stock
        stock_data = StockCreate(
            sku=created_product.sku,
            warehouse_id=created_warehouse.warehouse_id,
            quantity=50,
            min_stock=10,
            max_stock=100
        )
        
        created_stock = stock_crud.create(db_session, obj_in=stock_data)
        assert created_stock.stock_id is not None
        assert created_stock.quantity == 50
        
        # READ by SKU and Warehouse
        stock_by_sku_warehouse = stock_crud.get_by_sku_and_warehouse(
            db_session, 
            sku=created_product.sku, 
            warehouse_id=created_warehouse.warehouse_id
        )
        assert stock_by_sku_warehouse is not None
        assert stock_by_sku_warehouse.quantity == 50
        
        # GET by SKU (all warehouses)
        stock_by_sku = stock_crud.get_by_sku(db_session, sku=created_product.sku)
        assert len(stock_by_sku) > 0
        
        # LOW STOCK test
        # Actualizar a cantidad baja
        low_stock_update = StockUpdate(quantity=3)
        updated_stock = stock_crud.update(db_session, db_obj=created_stock, obj_in=low_stock_update)
        
        low_stock_items = stock_crud.get_low_stock(db_session, min_quantity=5)
        assert len(low_stock_items) > 0
        assert any(item.stock_id == updated_stock.stock_id for item in low_stock_items)
        
    def test_chat_crud_operations(self, db_session: Session):
        """Test operaciones CRUD para Chat Session y Message"""
        logger.info("Testing Chat CRUD operations")
        
        # Crear cliente primero
        client_data = {
            "name": "Cliente Chat CRUD",
            "email": "chatcrud@test.com",
            "phone": "987654321",
            "address": "Dirección Chat CRUD"
        }
        client = client_crud.create(db_session, obj_in=ClientCreate(**client_data))
        
        # Crear sesión de chat
        chat_session_data = {
            "chat_id": "CHATCRUD001",
            "client_id": client.client_id,
            "topic": "Test CRUD"
        }
        chat_session = chat_session_crud.create(db_session, obj_in=ChatSessionCreate(**chat_session_data))
        assert chat_session.chat_id == "CHATCRUD001"
        
        # Para el mensaje de chat, crear sin timestamp (que se auto-asigna)
        chat_message_data = {
            "chat_id": chat_session.chat_id,
            "sender": "cliente",
            "message_text": "Mensaje de prueba CRUD"
        }
        chat_message = chat_message_crud.create(db_session, obj_in=ChatMessageCreate(**chat_message_data))
        assert chat_message.sender == "cliente"
        assert chat_message.message_text == "Mensaje de prueba CRUD"
        assert chat_message.message_timestamp is not None  # Se auto-asigna
        
        logger.info("Chat CRUD operations successful")
        
    def test_knowledge_feedback_crud_operations(self, db_session: Session):
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
        
        created_feedback = knowledge_feedback_crud.create(db_session, obj_in=feedback_data)
        assert created_feedback.feedback_id is not None
        assert created_feedback.user_type == "cliente"
        assert created_feedback.status == "pendiente"
        
        # GET by status
        pending_feedback = knowledge_feedback_crud.get_pending_feedback(db_session)
        assert len(pending_feedback) > 0
        assert any(fb.feedback_id == created_feedback.feedback_id for fb in pending_feedback)
        
        # SEARCH by question
        search_results = knowledge_feedback_crud.search_by_question(db_session, question="configurar")
        assert len(search_results) > 0
        
    def test_crud_pagination(self, db_session: Session):
        """Test paginación en operaciones CRUD"""
        logger.info("Testing CRUD pagination")
        
        # Crear múltiples clientes para test de paginación
        from backend.db.schemas.client_schema import ClientCreate
        
        for i in range(5):
            client_data = ClientCreate(
                name=f"Cliente Paginación {i}",
                email=f"pag{i}@example.com",
                phone=f"12345678{i}",
                address=f"Dirección {i}",
                city=f"Ciudad {i}"
            )
            client_crud.create(db_session, obj_in=client_data)
        
        # Test paginación
        page_1 = client_crud.get_multi(db_session, skip=0, limit=3)
        page_2 = client_crud.get_multi(db_session, skip=3, limit=3)
        
        assert len(page_1) <= 3
        assert len(page_2) <= 3
        
        # Verificar que no hay duplicados entre páginas
        page_1_ids = {client.client_id for client in page_1}
        page_2_ids = {client.client_id for client in page_2}
        assert page_1_ids.isdisjoint(page_2_ids)
        
    def test_crud_error_handling(self, db_session: Session):
        """Test manejo de errores en operaciones CRUD"""
        logger.info("Testing CRUD error handling")
        
        # Test GET con ID inexistente
        non_existent_client = client_crud.get(db_session, client_id=99999)
        assert non_existent_client is None
        
        # Test DELETE con ID inexistente
        try:
            client_crud.remove(db_session, client_id=99999)
        except Exception:
            # Es esperado que falle al intentar eliminar algo que no existe
            pass
        
        logger.info("✅ CRUD error handling tests completed")