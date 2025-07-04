#backend/tests/conftest.py
pytest_plugins = ["pytest_asyncio"]

"""
Configuración de pytest para AInstalia
"""
import pytest
import tempfile
import os
import logging
from typing import AsyncGenerator
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from datetime import date, datetime
import json
import sqlite3
import anyio

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
async def async_test_db():
    """
    Fixture de base de datos de testing usando SQLite en memoria (async)
    """
    logger.info("Configurando base de datos de testing")
    
    # Crear motor de BD en memoria para tests con configuración especial para SQLite
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
        pool_pre_ping=True,
        pool_recycle=-1,
    )
    
    # Crear todas las tablas de forma asíncrona
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
        # Asynchronously get table names
        def get_table_names_sync(connection):
            from sqlalchemy import inspect as sync_inspect
            inspector = sync_inspect(connection)
            return inspector.get_table_names()

        tables = await conn.run_sync(get_table_names_sync)
    logger.info(f"Tablas creadas en test DB: {tables}")
    
    yield engine
    
    # Cleanup
    logger.info("Limpiando base de datos de testing")
    await engine.dispose()

@pytest.fixture(scope="function")
async def async_db_session(async_test_db: create_async_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture de sesión de BD asíncrona que se reinicia en cada test
    """
    async_session = async_sessionmaker(
        async_test_db, expire_on_commit=False, class_=AsyncSession
    )
    
    async with async_session() as session:
        # Esto establece un punto de guardado (savepoint) para cada test
        # y permite que los tests hagan rollback al final
        # sin afectar otros tests o el estado global de la base de datos.
        await session.begin()
        yield session
        await session.rollback()

@pytest.fixture
async def client(async_db_session: AsyncSession):
    """Test client con base de datos de test asíncrona"""
    from backend.main import app
    from backend.db.session import get_db
    
    async def override_get_db():
        yield async_db_session
    
    # Override de la dependencia de base de datos
    app.dependency_overrides[get_db] = override_get_db
    
    async with TestClient(app) as c:
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
        "user_type": "cliente",
        "question": "¿Cómo usar el producto?",
        "expected_answer": "Siga estos pasos...",
        "status": "pendiente"
    }

@pytest.fixture
def multiple_clients_data():
    """Datos de ejemplo para múltiples clientes"""
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
    """Datos de ejemplo para múltiples productos"""
    return [
        {
            "sku": f"PROD{i:03d}",
            "name": f"Producto {i}",
            "description": f"Descripción del producto {i}",
            "price": 10.0 + i,
            "spec_json": {"material": "plástico", "peso": f"{i}.0kg"}
        }
        for i in range(1, 6)
    ]

# ==========================================
# Fixtures de configuración
# ==========================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Fixture para configurar el logging durante los tests."""
    # Desactivar el logging en la consola para no interferir con la salida de pytest
    # durante los tests normales. Mantenerlo solo para fines de depuración si es necesario.
    logging.getLogger("ainstalia").setLevel(logging.CRITICAL)
    yield
    logging.getLogger("ainstalia").setLevel(logging.INFO) # Restaurar al final

@pytest.fixture
async def clean_database(async_db_session):
    """
    Fixture que garantiza una base de datos limpia.
    Útil para tests que requieren aislamiento total.
    """
    yield async_db_session
    
    # Limpiar todas las tablas después del test
    for table in reversed(Base.metadata.sorted_tables):
        await async_db_session.execute(table.delete())
    await async_db_session.commit() 