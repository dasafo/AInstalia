#backend/tests/phase_0/test_endpoints.py
"""
Tests para endpoints de la API FastAPI
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import Depends
from unittest.mock import patch
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from backend.main import app
from backend.db.session import get_db
from backend.crud import (
    client_crud, product_crud, warehouse_crud, stock_crud, technician_crud,
    equipment_crud, intervention_crud, contract_crud, chat_session_crud,
    chat_message_crud, knowledge_feedback_crud
)

from backend.schemas.client_schema import ClientCreate
from backend.schemas.product_schema import ProductCreate
from backend.schemas.warehouse_schema import WarehouseCreate
from backend.schemas.stock_schema import StockCreate
from backend.schemas.technician_schema import TechnicianCreate
from backend.schemas.equipment_schema import InstalledEquipmentCreate
from backend.schemas.intervention_schema import InterventionCreate
from backend.schemas.contract_schema import ContractCreate
from backend.schemas.chat_session_schema import ChatSessionCreate
from backend.schemas.chat_message_schema import ChatMessageCreate
from backend.schemas.knowledge_feedback_schema import KnowledgeFeedbackCreate

# ==========================================
# Tests de API Root
# ==========================================

def test_api_root(client: TestClient):
    """Test del endpoint raíz de la API"""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json() == {"message": "AInstalia API v1", "endpoints": "See /docs for full API documentation", "status": "active"}

def test_ping_endpoint(client: TestClient):
    """Test del endpoint ping"""
    response = client.get("/api/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}

# ==========================================
# Tests de Clientes
# ==========================================

def test_create_client(client: TestClient, sample_client_data: dict):
    """Test crear cliente"""
    response = client.post("/api/v1/clients/", json=sample_client_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_client_data["name"]
    assert data["email"] == sample_client_data["email"]
    assert "client_id" in data

def test_get_clients(client: TestClient, sample_client_data: dict):
    """Test obtener lista de clientes"""
    # Crear un cliente primero
    client.post("/api/v1/clients/", json=sample_client_data)
    
    response = client.get("/api/v1/clients/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == sample_client_data["name"]

def test_get_client_by_id(client: TestClient, sample_client_data: dict):
    """Test obtener cliente por ID"""
    # Crear cliente
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    created_client_id = client_response.json()["client_id"]
    
    response = client.get(f"/api/v1/clients/{created_client_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == created_client_id
    assert data["name"] == sample_client_data["name"]

def test_get_client_not_found(client: TestClient):
    """Test cliente no encontrado"""
    response = client.get("/api/v1/clients/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Cliente no encontrado"}

def test_update_client(client: TestClient, sample_client_data: dict):
    """Test actualizar cliente"""
    # Crear cliente
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    created_client_id = client_response.json()["client_id"]
    
    update_data = {"name": "Cliente Actualizado", "phone": "987654321"}
    response = client.put(f"/api/v1/clients/{created_client_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Cliente Actualizado"
    assert data["phone"] == "987654321"
    
    # Verificar que el email no ha cambiado
    assert data["email"] == sample_client_data["email"]

def test_delete_client(client: TestClient, sample_client_data: dict):
    """Test eliminar cliente"""
    # Crear cliente
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    created_client_id = client_response.json()["client_id"]
    
    response = client.delete(f"/api/v1/clients/{created_client_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == created_client_id
    assert data["name"] == sample_client_data["name"]
    
    # Verificar que el cliente fue eliminado
    get_response = client.get(f"/api/v1/clients/{created_client_id}")
    assert get_response.status_code == 404

# ==========================================
# Tests de Productos
# ==========================================

def test_create_product(client: TestClient, sample_product_data: dict):
    """Test crear producto"""
    response = client.post("/api/v1/products/", json=sample_product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == sample_product_data["sku"]
    assert data["name"] == sample_product_data["name"]
    assert "sku" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_products(client: TestClient, sample_product_data: dict):
    """Test obtener productos"""
    client.post("/api/v1/products/", json=sample_product_data)
    
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["sku"] == sample_product_data["sku"]

def test_get_product_by_sku(client: TestClient, sample_product_data: dict):
    """Test obtener producto por SKU"""
    client.post("/api/v1/products/", json=sample_product_data)
    
    response = client.get(f"/api/v1/products/{sample_product_data['sku']}")
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == sample_product_data["sku"]

# ==========================================
# Tests de Almacenes
# ==========================================

def test_create_warehouse(client: TestClient, sample_warehouse_data: dict):
    """Test crear almacén"""
    response = client.post("/api/v1/warehouses/", json=sample_warehouse_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_warehouse_data["name"]
    assert "warehouse_id" in data

def test_get_warehouses(client: TestClient, sample_warehouse_data: dict):
    """Test obtener almacenes"""
    client.post("/api/v1/warehouses/", json=sample_warehouse_data)
    
    response = client.get("/api/v1/warehouses/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == sample_warehouse_data["name"]

# ==========================================
# Tests de Stock
# ==========================================

def test_create_stock(client: TestClient, sample_stock_data: dict, sample_warehouse_data: dict, sample_product_data: dict):
    """Test crear registro de stock"""
    # Crear dependencias primero
    warehouse_response = client.post("/api/v1/warehouses/", json=sample_warehouse_data)
    product_response = client.post("/api/v1/products/", json=sample_product_data)
    
    sample_stock_data["warehouse_id"] = warehouse_response.json()["warehouse_id"]
    sample_stock_data["sku"] = product_response.json()["sku"]
    
    response = client.post("/api/v1/stock/", json=sample_stock_data)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == sample_stock_data["quantity"]
    assert "stock_id" in data

def test_get_stock_with_filters(client: TestClient, sample_stock_data: dict, sample_warehouse_data: dict, sample_product_data: dict):
    """Test obtener stock con filtros"""
    # Crear dependencias
    warehouse_response = client.post("/api/v1/warehouses/", json=sample_warehouse_data)
    product_response = client.post("/api/v1/products/", json=sample_product_data)
    
    sample_stock_data["warehouse_id"] = warehouse_response.json()["warehouse_id"]
    sample_stock_data["sku"] = product_response.json()["sku"]
    
    client.post("/api/v1/stock/", json=sample_stock_data)
    
    # Test con filtros
    response = client.get(f"/api/v1/stock/?warehouse_id={sample_stock_data['warehouse_id']}&sku={sample_stock_data['sku']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["quantity"] == sample_stock_data["quantity"]

# ==========================================
# Tests de Técnicos
# ==========================================

def test_create_technician(client: TestClient, sample_technician_data: dict):
    """Test crear técnico"""
    response = client.post("/api/v1/technicians/", json=sample_technician_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_technician_data["name"]
    assert "technician_id" in data

def test_get_technicians(client: TestClient, sample_technician_data: dict):
    """Test obtener técnicos"""
    client.post("/api/v1/technicians/", json=sample_technician_data)
    
    response = client.get("/api/v1/technicians/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == sample_technician_data["name"]

# ==========================================
# Tests de Equipos
# ==========================================

def test_create_equipment(client: TestClient, sample_equipment_data: dict, sample_client_data: dict, sample_product_data: dict):
    """Test crear equipo instalado"""
    # Crear dependencias
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    product_response = client.post("/api/v1/products/", json=sample_product_data)
    
    sample_equipment_data["client_id"] = client_response.json()["client_id"]
    sample_equipment_data["sku"] = product_response.json()["sku"]
    
    response = client.post("/api/v1/equipment/", json=sample_equipment_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == sample_equipment_data["status"]
    assert "equipment_id" in data

# ==========================================
# Tests de Intervenciones
# ==========================================

def test_create_intervention(client: TestClient, sample_intervention_data: dict, sample_client_data: dict, sample_technician_data: dict):
    """Test crear intervención"""
    # Crear dependencias
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    technician_response = client.post("/api/v1/technicians/", json=sample_technician_data)
    
    sample_intervention_data["client_id"] = client_response.json()["client_id"]
    sample_intervention_data["technician_id"] = technician_response.json()["technician_id"]

    # Crear equipo (intervención requiere equipment_id)
    # Usamos un producto y cliente dummy para crear un equipo si no hay uno disponible
    dummy_product = ProductCreate(sku="DUMMY-PROD", name="Dummy Product", price=1.0)
    dummy_client = ClientCreate(name="Dummy Client", email="dummy@example.com", phone="123456789", address="Dummy Address")
    
    dummy_client_res = client.post("/api/v1/clients/", json=dummy_client.model_dump())
    dummy_product_res = client.post("/api/v1/products/", json=dummy_product.model_dump())
    
    dummy_equipment_data = {
        "client_id": dummy_client_res.json()["client_id"],
        "sku": dummy_product_res.json()["sku"],
        "install_date": "2023-01-01",
        "status": "activo",
        "config_json": {}
    }
    dummy_equipment_res = client.post("/api/v1/equipment/", json=dummy_equipment_data)
    sample_intervention_data["equipment_id"] = dummy_equipment_res.json()["equipment_id"]
    
    response = client.post("/api/v1/interventions/", json=sample_intervention_data)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == sample_intervention_data["type"]
    assert "intervention_id" in data

def test_get_interventions_by_technician(client: TestClient, sample_intervention_data: dict, sample_client_data: dict, sample_technician_data: dict):
    """Test obtener intervenciones por técnico"""
    # Crear dependencias
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    technician_response = client.post("/api/v1/technicians/", json=sample_technician_data)
    
    sample_intervention_data["client_id"] = client_response.json()["client_id"]
    sample_intervention_data["technician_id"] = technician_response.json()["technician_id"]
    
    # Crear equipo dummy
    dummy_product = ProductCreate(sku="DUMMY-PROD-2", name="Dummy Product 2", price=1.0)
    dummy_client = ClientCreate(name="Dummy Client 2", email="dummy2@example.com", phone="987654321", address="Dummy Address 2")
    
    dummy_client_res = client.post("/api/v1/clients/", json=dummy_client.model_dump())
    dummy_product_res = client.post("/api/v1/products/", json=dummy_product.model_dump())
    
    dummy_equipment_data = {
        "client_id": dummy_client_res.json()["client_id"],
        "sku": dummy_product_res.json()["sku"],
        "install_date": "2023-01-01",
        "status": "activo",
        "config_json": {}
    }
    dummy_equipment_res = client.post("/api/v1/equipment/", json=dummy_equipment_data)
    sample_intervention_data["equipment_id"] = dummy_equipment_res.json()["equipment_id"]
    
    client.post("/api/v1/interventions/", json=sample_intervention_data)
    
    response = client.get(f"/api/v1/interventions/?technician_id={sample_intervention_data['technician_id']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["type"] == sample_intervention_data["type"]

# ==========================================
# Tests de Contratos
# ==========================================

def test_create_contract(client: TestClient, sample_contract_data: dict, sample_client_data: dict):
    """Test crear contrato"""
    # Crear cliente
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    sample_contract_data["client_id"] = client_response.json()["client_id"]
    
    response = client.post("/api/v1/contracts/", json=sample_contract_data)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == sample_contract_data["type"]
    assert "contract_id" in data

def test_get_contracts_by_client(client: TestClient, sample_contract_data: dict, sample_client_data: dict):
    """Test obtener contratos por cliente"""
    # Crear cliente
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    sample_contract_data["client_id"] = client_response.json()["client_id"]
    
    client.post("/api/v1/contracts/", json=sample_contract_data)
    
    response = client.get(f"/api/v1/contracts/?client_id={sample_contract_data['client_id']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["type"] == sample_contract_data["type"]

# ==========================================
# Tests de Chat
# ==========================================

def test_create_chat_session(client: TestClient, sample_chat_session_data: dict, sample_client_data: dict):
    """Test crear sesión de chat"""
    # Crear cliente
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    sample_chat_session_data["client_id"] = client_response.json()["client_id"]
    
    response = client.post("/api/v1/chat/sessions/", json=sample_chat_session_data)
    assert response.status_code == 200
    data = response.json()
    assert data["chat_id"] == sample_chat_session_data["chat_id"]
    assert "chat_id" in data

async def test_create_chat_message(client: TestClient, sample_chat_session_data: dict, sample_chat_message_data: dict, async_db_session: AsyncSession):
    """Test crear mensaje de chat"""
    # Primero crear chat session usando el crud asíncrono
    # Necesitamos un client_id existente para la sesión de chat
    client_data = ClientCreate(name="Test Client for Chat", email="chat@example.com", phone="123456789", address="Chat Address")
    created_client = await client_crud.create(async_db_session, obj_in=client_data)

    sample_chat_session_data["client_id"] = created_client.client_id
    chat_session = await chat_session_crud.create(db=async_db_session, obj_in=ChatSessionCreate(**sample_chat_session_data))
    
    # Crear mensaje de chat
    response = client.post("/api/v1/chat/messages/", json=sample_chat_message_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message_text"] == sample_chat_message_data["message_text"]
    assert "message_id" in data

async def test_get_chat_messages_by_session(client: TestClient, sample_chat_session_data: dict, sample_chat_message_data: dict, async_db_session: AsyncSession):
    """Test obtener mensajes por sesión de chat"""
    # Crear chat session y mensaje usando los crud asíncronos
    client_data = ClientCreate(name="Test Client for Chat 2", email="chat2@example.com", phone="987654321", address="Chat Address 2")
    created_client = await client_crud.create(async_db_session, obj_in=client_data)

    sample_chat_session_data["client_id"] = created_client.client_id
    chat_session = await chat_session_crud.create(db=async_db_session, obj_in=ChatSessionCreate(**sample_chat_session_data))
    chat_message = await chat_message_crud.create(db=async_db_session, obj_in=ChatMessageCreate(**sample_chat_message_data))
    
    # Obtener mensajes
    chat_id = sample_chat_session_data["chat_id"]
    response = client.get(f"/api/v1/chat/messages/session/{chat_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["message_text"] == sample_chat_message_data["message_text"]

# ==========================================
# Tests de Knowledge Feedback
# ==========================================

def test_create_knowledge_feedback(client: TestClient, sample_knowledge_feedback_data: dict):
    """Test crear feedback de conocimiento"""
    response = client.post("/api/v1/knowledge/", json=sample_knowledge_feedback_data)
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == sample_knowledge_feedback_data["question"]
    assert "feedback_id" in data

def test_get_knowledge_feedback_by_user_type(client: TestClient, sample_knowledge_feedback_data: dict):
    """Test filtrar feedback por tipo de usuario"""
    # Crear feedback
    client.post("/api/v1/knowledge/", json=sample_knowledge_feedback_data)
    
    response = client.get(f"/api/v1/knowledge/?user_type={sample_knowledge_feedback_data['user_type']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["user_type"] == sample_knowledge_feedback_data["user_type"]

def test_get_knowledge_feedback_by_status(client: TestClient, sample_knowledge_feedback_data: dict):
    """Test filtrar feedback por estado"""
    # Crear feedback
    client.post("/api/v1/knowledge/", json=sample_knowledge_feedback_data)
    
    response = client.get(f"/api/v1/knowledge/?status={sample_knowledge_feedback_data['status']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["status"] == sample_knowledge_feedback_data["status"]

# ==========================================
# Tests de Paginación
# ==========================================

def test_clients_pagination(client: TestClient, multiple_clients_data: list):
    """Test paginación en clientes"""
    # Crear múltiples clientes
    for client_data in multiple_clients_data:
        client.post("/api/v1/clients/", json=client_data)

    # Test paginación
    response_page_1 = client.get("/api/v1/clients/?skip=0&limit=3")
    assert response_page_1.status_code == 200
    page_1_data = response_page_1.json()
    assert len(page_1_data) == 3

    response_page_2 = client.get("/api/v1/clients/?skip=3&limit=3")
    assert response_page_2.status_code == 200
    page_2_data = response_page_2.json()
    assert len(page_2_data) == 2 # Remaining 2 clients

    # Verificar que los datos son los esperados (ordenados por client_id o similar)
    all_clients_response = client.get("/api/v1/clients/")
    all_clients = all_clients_response.json()
    assert len(all_clients) == 5

def test_pagination_limits(client: TestClient, sample_client_data: dict):
    """Test límites de paginación"""
    # Crear cliente
    client.post("/api/v1/clients/", json=sample_client_data)

    # Test límite máximo (ej. si el límite por defecto es 100, pedir 200 debería devolver 100)
    response = client.get("/api/v1/clients/?limit=200")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 100 # Asumiendo un límite máximo de 100 en la API

    # Test límite negativo (debería dar error de validación)
    response_invalid_limit = client.get("/api/v1/clients/?limit=-1")
    assert response_invalid_limit.status_code == 422 # Unprocessable Entity

def test_create_client_invalid_email(client: TestClient):
    """Test crear cliente con email inválido"""
    invalid_data = {
        "name": "Cliente Test",
        "email": "email-invalido",  # Email sin formato válido
        "phone": "123456789",
        "address": "Dirección Test"
    }
    response = client.post("/api/v1/clients/", json=invalid_data)
    assert response.status_code == 422 # Unprocessable Entity
    assert "Formato de email inválido" in response.json()["detail"][0]["msg"]

def test_create_client_missing_required_fields(client: TestClient):
    """Test crear cliente sin campos requeridos"""
    incomplete_data = {
        "name": "Cliente Test"
        # Faltan campos requeridos
    }
    response = client.post("/api/v1/clients/", json=incomplete_data)
    assert response.status_code == 422 # Unprocessable Entity
    # Asegúrate de que los mensajes de error de Pydantic sean los esperados 