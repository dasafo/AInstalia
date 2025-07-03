#backend/tests/phase_0/test_endpoints.py
"""
Tests para endpoints de la API FastAPI
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import Depends
from unittest.mock import patch
from sqlalchemy.orm import Session

from backend.main import app
from backend.db.session import get_db

# ==========================================
# Tests de API Root
# ==========================================

def test_api_root(client):
    """Test del endpoint raíz de la API"""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "AInstalia API v1"
    assert data["status"] == "active"

def test_ping_endpoint(client):
    """Test del endpoint ping"""
    response = client.get("/api/v1/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "pong"

# ==========================================
# Tests de Clientes
# ==========================================

def test_create_client(client, sample_client_data):
    """Test crear cliente"""
    response = client.post("/api/v1/clients/", json=sample_client_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_client_data["name"]
    assert data["email"] == sample_client_data["email"]
    assert "client_id" in data

def test_get_clients(client, sample_client_data):
    """Test obtener lista de clientes"""
    # Crear un cliente primero
    client.post("/api/v1/clients/", json=sample_client_data)
    
    # Obtener lista
    response = client.get("/api/v1/clients/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_client_by_id(client, sample_client_data):
    """Test obtener cliente por ID"""
    # Crear cliente
    create_response = client.post("/api/v1/clients/", json=sample_client_data)
    client_id = create_response.json()["client_id"]
    
    # Obtener por ID
    response = client.get(f"/api/v1/clients/{client_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == client_id
    assert data["name"] == sample_client_data["name"]

def test_get_client_not_found(client):
    """Test cliente no encontrado"""
    response = client.get("/api/v1/clients/99999")
    assert response.status_code == 404

def test_update_client(client, sample_client_data):
    """Test actualizar cliente"""
    # Crear cliente
    create_response = client.post("/api/v1/clients/", json=sample_client_data)
    client_id = create_response.json()["client_id"]
    
    # Actualizar
    update_data = {"name": "Cliente Actualizado"}
    response = client.put(f"/api/v1/clients/{client_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Cliente Actualizado"

def test_delete_client(client, sample_client_data):
    """Test eliminar cliente"""
    # Crear cliente
    create_response = client.post("/api/v1/clients/", json=sample_client_data)
    client_id = create_response.json()["client_id"]
    
    # Eliminar
    response = client.delete(f"/api/v1/clients/{client_id}")
    assert response.status_code == 200
    
    # Verificar que ya no existe
    get_response = client.get(f"/api/v1/clients/{client_id}")
    assert get_response.status_code == 404

# ==========================================
# Tests de Productos
# ==========================================

def test_create_product(client, sample_product_data):
    """Test crear producto"""
    response = client.post("/api/v1/products/", json=sample_product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_product_data["name"]
    assert data["sku"] == sample_product_data["sku"]

def test_get_products(client, sample_product_data):
    """Test obtener productos"""
    client.post("/api/v1/products/", json=sample_product_data)
    
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_product_by_sku(client, sample_product_data):
    """Test obtener producto por SKU"""
    client.post("/api/v1/products/", json=sample_product_data)
    sku = sample_product_data["sku"]
    
    response = client.get(f"/api/v1/products/{sku}")
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == sku

# ==========================================
# Tests de Almacenes
# ==========================================

def test_create_warehouse(client, sample_warehouse_data):
    """Test crear almacén"""
    response = client.post("/api/v1/warehouses/", json=sample_warehouse_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_warehouse_data["name"]
    assert "warehouse_id" in data

def test_get_warehouses(client, sample_warehouse_data):
    """Test obtener almacenes"""
    client.post("/api/v1/warehouses/", json=sample_warehouse_data)
    
    response = client.get("/api/v1/warehouses/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# ==========================================
# Tests de Stock
# ==========================================

def test_create_stock(client, sample_stock_data, sample_warehouse_data, sample_product_data):
    """Test crear registro de stock"""
    # Crear dependencias primero
    warehouse_response = client.post("/api/v1/warehouses/", json=sample_warehouse_data)
    warehouse_id = warehouse_response.json()["warehouse_id"]
    
    client.post("/api/v1/products/", json=sample_product_data)
    
    # Crear stock
    stock_data = {**sample_stock_data, "warehouse_id": warehouse_id}
    response = client.post("/api/v1/stock/", json=stock_data)
    assert response.status_code == 200
    data = response.json()
    assert data["warehouse_id"] == warehouse_id

def test_get_stock_with_filters(client, sample_stock_data, sample_warehouse_data, sample_product_data):
    """Test obtener stock con filtros"""
    # Crear dependencias
    warehouse_response = client.post("/api/v1/warehouses/", json=sample_warehouse_data)
    warehouse_id = warehouse_response.json()["warehouse_id"]
    client.post("/api/v1/products/", json=sample_product_data)
    
    # Crear stock
    stock_data = {**sample_stock_data, "warehouse_id": warehouse_id}
    client.post("/api/v1/stock/", json=stock_data)
    
    # Filtrar por warehouse
    response = client.get(f"/api/v1/stock/?warehouse_id={warehouse_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# ==========================================
# Tests de Técnicos
# ==========================================

def test_create_technician(client, sample_technician_data):
    """Test crear técnico"""
    response = client.post("/api/v1/technicians/", json=sample_technician_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_technician_data["name"]
    assert data["email"] == sample_technician_data["email"]

def test_get_technicians(client, sample_technician_data):
    """Test obtener técnicos"""
    client.post("/api/v1/technicians/", json=sample_technician_data)
    
    response = client.get("/api/v1/technicians/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# ==========================================
# Tests de Equipos
# ==========================================

def test_create_equipment(client, sample_equipment_data, sample_client_data, sample_product_data):
    """Test crear equipo instalado"""
    # Crear dependencias
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    client_id = client_response.json()["client_id"]
    
    client.post("/api/v1/products/", json=sample_product_data)
    
    # Crear equipo
    equipment_data = {**sample_equipment_data, "client_id": client_id}
    response = client.post("/api/v1/equipment/", json=equipment_data)
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == client_id

# ==========================================
# Tests de Intervenciones
# ==========================================

def test_create_intervention(client, sample_intervention_data, sample_client_data, sample_technician_data):
    """Test crear intervención"""
    # Crear dependencias
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    client_id = client_response.json()["client_id"]
    
    technician_response = client.post("/api/v1/technicians/", json=sample_technician_data)
    technician_id = technician_response.json()["technician_id"]
    
    # Crear intervención
    intervention_data = {
        **sample_intervention_data, 
        "client_id": client_id,
        "technician_id": technician_id
    }
    response = client.post("/api/v1/interventions/", json=intervention_data)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Data sent: {intervention_data}")
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == client_id
    assert data["technician_id"] == technician_id

def test_get_interventions_by_technician(client, sample_intervention_data, sample_client_data, sample_technician_data):
    """Test obtener intervenciones por técnico"""
    # Crear dependencias
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    client_id = client_response.json()["client_id"]
    
    technician_response = client.post("/api/v1/technicians/", json=sample_technician_data)
    technician_id = technician_response.json()["technician_id"]
    
    # Crear intervención
    intervention_data = {
        **sample_intervention_data, 
        "client_id": client_id,
        "technician_id": technician_id
    }
    client.post("/api/v1/interventions/", json=intervention_data)
    
    # Obtener por técnico
    response = client.get(f"/api/v1/interventions/?technician_id={technician_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# ==========================================
# Tests de Contratos
# ==========================================

def test_create_contract(client, sample_contract_data, sample_client_data):
    """Test crear contrato"""
    # Crear cliente
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    client_id = client_response.json()["client_id"]
    
    # Crear contrato
    contract_data = {**sample_contract_data, "client_id": client_id}
    response = client.post("/api/v1/contracts/", json=contract_data)
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == client_id

def test_get_contracts_by_client(client, sample_contract_data, sample_client_data):
    """Test obtener contratos por cliente"""
    # Crear cliente
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    client_id = client_response.json()["client_id"]
    
    # Crear contrato
    contract_data = {**sample_contract_data, "client_id": client_id}
    client.post("/api/v1/contracts/", json=contract_data)
    
    # Obtener contratos del cliente
    response = client.get(f"/api/v1/contracts/?client_id={client_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# ==========================================
# Tests de Chat
# ==========================================

def test_create_chat_session(client, sample_chat_session_data, sample_client_data):
    """Test crear sesión de chat"""
    # Crear cliente
    client_response = client.post("/api/v1/clients/", json=sample_client_data)
    client_id = client_response.json()["client_id"]
    
    # Crear sesión de chat
    chat_data = {**sample_chat_session_data, "client_id": client_id}
    response = client.post("/api/v1/chat/sessions/", json=chat_data)
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == client_id

def test_create_chat_message(client, db_session, sample_chat_session_data, sample_chat_message_data):
    """Test crear mensaje de chat"""
    # Primero crear chat session
    from backend.crud import chat_session_crud
    chat_session = chat_session_crud.create(db=db_session, obj_in=sample_chat_session_data)
    
    # Crear mensaje de chat
    response = client.post("/api/v1/chat/messages/", json=sample_chat_message_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["chat_id"] == sample_chat_message_data["chat_id"]
    assert data["sender"] == sample_chat_message_data["sender"]
    assert data["message_text"] == sample_chat_message_data["message_text"]

def test_get_chat_messages_by_session(client, db_session, sample_chat_session_data, sample_chat_message_data):
    """Test obtener mensajes por sesión de chat"""
    # Crear chat session y mensaje
    from backend.crud import chat_session_crud, chat_message_crud
    chat_session = chat_session_crud.create(db=db_session, obj_in=sample_chat_session_data)
    chat_message = chat_message_crud.create(db=db_session, obj_in=sample_chat_message_data)
    
    # Obtener mensajes
    chat_id = sample_chat_session_data["chat_id"]
    response = client.get(f"/api/v1/chat/messages/session/{chat_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) >= 1
    assert data[0]["chat_id"] == chat_id

# ==========================================
# Tests de Knowledge Feedback
# ==========================================

def test_create_knowledge_feedback(client, sample_knowledge_feedback_data):
    """Test crear feedback de conocimiento"""
    response = client.post("/api/v1/knowledge/", json=sample_knowledge_feedback_data)
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == sample_knowledge_feedback_data["question"]
    assert data["user_type"] == sample_knowledge_feedback_data["user_type"]

def test_get_knowledge_feedback_by_user_type(client, sample_knowledge_feedback_data):
    """Test filtrar feedback por tipo de usuario"""
    # Crear feedback
    client.post("/api/v1/knowledge/", json=sample_knowledge_feedback_data)
    
    # Filtrar por user_type
    user_type = sample_knowledge_feedback_data["user_type"]
    response = client.get(f"/api/v1/knowledge/?user_type={user_type}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_knowledge_feedback_by_status(client, sample_knowledge_feedback_data):
    """Test filtrar feedback por estado"""
    # Crear feedback
    client.post("/api/v1/knowledge/", json=sample_knowledge_feedback_data)
    
    # Filtrar por status
    status = sample_knowledge_feedback_data["status"]
    response = client.get(f"/api/v1/knowledge/?status={status}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# ==========================================
# Tests de Paginación
# ==========================================

def test_clients_pagination(client, multiple_clients_data):
    """Test paginación en clientes"""
    # Crear múltiples clientes
    for client_data in multiple_clients_data:
        client.post("/api/v1/clients/", json=client_data)
    
    # Test paginación
    response = client.get("/api/v1/clients/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2

def test_pagination_limits(client, sample_client_data):
    """Test límites de paginación"""
    # Crear cliente
    client.post("/api/v1/clients/", json=sample_client_data)
    
    # Test límite máximo
    response = client.get("/api/v1/clients/?limit=1001")
    assert response.status_code == 422  # Validation error

    # Test límite válido
    response = client.get("/api/v1/clients/?limit=100")
    assert response.status_code == 200

# ==========================================
# Tests de Validación de Datos
# ==========================================

def test_create_client_invalid_email(client):
    """Test crear cliente con email inválido"""
    invalid_data = {
        "name": "Cliente Test",
        "email": "email-invalido",  # Email sin formato válido
        "phone": "123456789",
        "address": "Dirección Test"
    }
    response = client.post("/api/v1/clients/", json=invalid_data)
    assert response.status_code == 422

def test_create_client_missing_required_fields(client):
    """Test crear cliente sin campos requeridos"""
    incomplete_data = {
        "name": "Cliente Test"
        # Faltan campos requeridos
    }
    response = client.post("/api/v1/clients/", json=incomplete_data)
    assert response.status_code == 422 