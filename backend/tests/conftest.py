#backend/tests/conftest.py
"""
Configuración de pytest para AInstalia
"""
import pytest
import tempfile
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from datetime import date, datetime
import json
import sqlite3
from typing import Generator

from backend.db.base import Base
from backend.core.logging import get_logger

# Importar todos los modelos para que SQLAlchemy los registre
from backend.models.client_model import Client
from backend.models.product_model import Product
from backend.models.warehouse_model import Warehouse
from backend.models.stock_model import Stock
from backend.models.technician_model import Technician
from backend.models.equipment_model import InstalledEquipment
from backend.models.intervention_model import Intervention
from backend.models.contract_model import Contract
from backend.models.chat_session_model import ChatSession
from backend.models.chat_message_model import ChatMessage
from backend.models.knowledge_feedback_model import KnowledgeFeedback

logger = get_logger("ainstalia.tests")

@pytest.fixture(scope="function")
def test_db():
    """
    Fixture de base de datos de testing usando SQLite en memoria
    """
    logger.info("Configurando base de datos de testing")
    
    # Crear motor de BD en memoria para tests con configuración especial para SQLite
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,  # Cambiar a True para ver SQL queries
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
        pool_pre_ping=True,
        pool_recycle=-1,
    )
    
    # Crear todas las tablas - IMPORTANTE: llamar después de importar modelos
    Base.metadata.create_all(bind=engine)
    
    # Verificar que las tablas se crearon
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Tablas creadas en test DB: {tables}")
    
    yield engine
    
    # Cleanup
    logger.info("Limpiando base de datos de testing")
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(test_db):
    """
    Fixture de sesión de BD que se reinicia en cada test
    """
    # Usar el engine de test directamente
    connection = test_db.connect()
    transaction = connection.begin()
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def client(test_db):
    """Test client con base de datos de test"""
    from backend.main import app
    from backend.db.session import get_db
    
    # Crear sessionmaker para tests usando el mismo engine
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    # Override de la dependencia de base de datos
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    # Limpiar overrides
    app.dependency_overrides.clear()

# ==========================================
# Fixtures de datos de prueba
# ==========================================

@pytest.fixture
def sample_client_data():
    """Datos de ejemplo para Client"""
    return {
        "name": "Cliente Test",
        "email": "test@example.com",
        "phone": "123456789",
        "address": "Dirección Test 123"
    }

@pytest.fixture
def sample_product_data():
    """Datos de ejemplo para Product"""
    return {
        "sku": "TEST-SKU-001",
        "name": "Producto Test",
        "description": "Descripción del producto de prueba",
        "price": 99.99,
        "spec_json": {"color": "azul", "tamaño": "mediano"}
    }

@pytest.fixture
def sample_warehouse_data():
    """Datos de ejemplo para Warehouse"""
    return {
        "name": "Almacén Test"
    }

@pytest.fixture
def sample_technician_data():
    """Datos de muestra para Technician"""
    return {
        "name": "Técnico Test",
        "email": "tecnico@test.com",
        "phone": "987654321",
        "zone": "Zona Norte"
    }

@pytest.fixture
def sample_equipment_data():
    """Datos de muestra para Equipment"""
    return {
        "client_id": 1,
        "sku": "TEST-SKU-001",
        "install_date": "2024-01-15",
        "status": "activo",
        "config_json": {"configuracion": "test"}
    }

@pytest.fixture
def sample_intervention_data():
    """Datos de muestra para Intervention"""
    return {
        "client_id": 1,
        "equipment_id": 1,
        "scheduled_date": "2024-06-15",
        "type": "mantenimiento",
        "description": "Mantenimiento preventivo"
    }

@pytest.fixture
def sample_contract_data():
    """Datos de muestra para Contract"""
    return {
        "client_id": 1,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "type": "mantenimiento",
        "terms": "Términos y condiciones del contrato"
    }

@pytest.fixture
def sample_stock_data():
    """Datos de muestra para Stock"""
    return {
        "sku": "TEST-SKU-STOCK",
        "warehouse_id": 1,
        "quantity": 25
    }

@pytest.fixture
def sample_chat_session_data():
    """Datos de muestra para Chat Session"""
    return {
        "chat_id": "CHAT-TEST-001",
        "order_id": None,
        "client_id": 1,
        "topic": "Soporte Test"
    }

@pytest.fixture
def sample_chat_message_data():
    """Datos de muestra para Chat Message"""
    return {
        "chat_id": "CHAT-TEST-001",
        "sender": "cliente",
        "message_text": "Mensaje de test"
    }

@pytest.fixture
def sample_knowledge_feedback_data():
    """Datos de muestra para Knowledge Feedback"""
    return {
        "question": "¿Cómo usar el producto?",
        "expected_answer": "Siga estos pasos...",
        "user_type": "cliente",
        "status": "pendiente"
    }

@pytest.fixture
def multiple_clients_data():
    """Múltiples clientes para tests de paginación y búsqueda"""
    return [
        {
            "name": f"Cliente {i}",
            "email": f"cliente{i}@example.com",
            "phone": f"12345678{i}",
            "address": f"Dirección {i}"
        }
        for i in range(1, 6)
    ]

@pytest.fixture
def multiple_products_data():
    """Múltiples productos para tests"""
    return [
        {
            "sku": f"SKU-{i:03d}",
            "name": f"Producto {i}",
            "description": f"Descripción producto {i}",
            "price": 10.0 * i,
            "spec_json": {"category": "Test"}
        }
        for i in range(1, 6)
    ]

# ==========================================
# Fixtures de configuración
# ==========================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Configura logging para tests"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger.info("🧪 Starting AInstalia test suite")
    yield
    logger.info("✅ AInstalia test suite completed")

@pytest.fixture
def clean_database(db_session):
    """
    Fixture que garantiza una base de datos limpia.
    Útil para tests que requieren aislamiento total.
    """
    yield db_session
    
    # Limpiar todas las tablas después del test
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit() 