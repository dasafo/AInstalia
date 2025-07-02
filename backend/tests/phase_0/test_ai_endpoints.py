#backend/tests/phase_0/test_ai_endpoints.py
"""
Tests para los endpoints de IA
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from backend.schemas.ai_schema import UserRole

from backend.core.config import settings


class TestAIEndpoints:
    """Test class para los endpoints de IA"""

    def test_sql_query_success(self, client: TestClient):
        """Test consulta SQL exitosa"""
        
        # Mock del servicio de IA completo
        with patch('backend.api.v1.endpoints.ai.get_ai_service') as mock_service:
            mock_ai_service = MagicMock()
            mock_ai_service.execute_sql_query = AsyncMock(return_value={
                "success": True,
                "result": [{"total_clients": 5}],
                "total_results": 1,
                "error": None,
                "sql_query": "SELECT COUNT(*) as total_clients FROM clients",
                "user_role": "administrador"
            })
            mock_service.return_value = mock_ai_service

            response = client.post(
                "/api/v1/ai/sql-query",
                json={
                    "query": "¿Cuántos clientes tenemos?",
                    "user_role": "administrador",
                    "user_id": None,
                    "include_sql": True
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"][0]["total_clients"] == 5
        assert data["total_results"] == 1
        assert data["sql_query"] == "SELECT COUNT(*) as total_clients FROM clients"
        assert data["user_role"] == "administrador"
        assert "execution_time_ms" in data

    def test_sql_query_error(self, client: TestClient):
        """Test consulta SQL con error"""
        
        with patch('backend.api.v1.endpoints.ai.get_ai_service') as mock_service:
            mock_ai_service = MagicMock()
            mock_ai_service.execute_sql_query = AsyncMock(return_value={
                "success": False,
                "result": None,
                "total_results": None,
                "error": "Error de sintaxis SQL",
                "sql_query": None,
                "user_role": "cliente"
            })
            mock_service.return_value = mock_ai_service

            response = client.post(
                "/api/v1/ai/sql-query",
                json={
                    "query": "consulta mal formada",
                    "user_role": "cliente",
                    "user_id": 1,
                    "include_sql": False
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "Error de sintaxis SQL"
        assert data["result"] is None

    def test_sql_query_without_sql_included(self, client: TestClient):
        """Test consulta SQL sin incluir el SQL generado"""
        
        with patch('backend.api.v1.endpoints.ai.get_ai_service') as mock_service:
            mock_ai_service = MagicMock()
            mock_ai_service.execute_sql_query = AsyncMock(return_value={
                "success": True,
                "result": [{"total_orders": 10}],
                "total_results": 1,
                "error": None,
                "sql_query": "SELECT COUNT(*) FROM orders",
                "user_role": "tecnico"
            })
            mock_service.return_value = mock_ai_service

            response = client.post(
                "/api/v1/ai/sql-query",
                json={
                    "query": "¿Cuántas órdenes hay?",
                    "user_role": "tecnico",
                    "user_id": 123,
                    "include_sql": False
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"][0]["total_orders"] == 10
        # No debe incluir SQL cuando include_sql=False
        assert data.get("sql_query") is None

    def test_business_insights_success(self, client: TestClient):
        """Test obtener insights de negocio exitoso"""
        
        with patch('backend.api.v1.endpoints.ai.get_ai_service') as mock_service:
            mock_ai_service = MagicMock()
            mock_ai_service.get_business_insights = AsyncMock(return_value={
                "success": True,
                "insights": {
                    "total_clients": [{"total": 25}],
                    "total_orders": [{"total": 150}],
                    "pending_interventions": [{"total": 5}]
                },
                "user_role": "administrador"
            })
            mock_service.return_value = mock_ai_service

            response = client.get(
                "/api/v1/ai/insights?user_role=administrador"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_clients" in data["insights"]
        assert data["user_role"] == "administrador"

    def test_business_insights_forbidden_for_non_admin(self, client: TestClient):
        """Test que no-admin no puede acceder a insights"""
        response = client.get("/api/v1/ai/insights?user_role=cliente")
        
        assert response.status_code == 403
        data = response.json()
        assert "Solo los administradores" in data["detail"]

    def test_business_insights_forbidden_for_technician(self, client: TestClient):
        """Test que técnico no puede acceder a insights"""
        response = client.get("/api/v1/ai/insights?user_role=tecnico")
        
        assert response.status_code == 403
        data = response.json()
        assert "Solo los administradores" in data["detail"]

    def test_knowledge_query_not_implemented(self, client: TestClient):
        """Test consulta de conocimiento no implementada"""
        response = client.post(
            "/api/v1/ai/knowledge-query",
            json={
                "query": "¿Cómo funciona el sistema?",
                "context": "general",
                "include_sources": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "en desarrollo" in data["error"]

    def test_submit_feedback_success(self, client: TestClient):
        """Test envío de feedback exitoso"""
        
        feedback_data = {
            "original_query": "¿Cuántos clientes tenemos?",
            "ai_response": "Tenemos 25 clientes",
            "user_feedback": "La respuesta fue correcta y útil",
            "rating": 5,
            "user_type": "administrador"
        }

        # Mock del CRUD de feedback
        with patch('backend.api.v1.endpoints.ai.CRUDKnowledgeFeedback') as mock_crud_class:
            mock_crud_instance = MagicMock()
            mock_crud_instance.create.return_value = MagicMock(id=123)
            mock_crud_class.return_value = mock_crud_instance

            response = client.post(
                "/api/v1/ai/feedback",
                json=feedback_data
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["feedback_id"] == 123
        assert "Feedback recibido correctamente" in data["message"]

    def test_submit_feedback_error(self, client: TestClient):
        """Test error al enviar feedback"""
        
        feedback_data = {
            "original_query": "Test query",
            "ai_response": "Test response", 
            "user_feedback": "Test feedback",
            "rating": 3,
            "user_type": "cliente"
        }

        # Mock del CRUD con error
        with patch('backend.api.v1.endpoints.ai.CRUDKnowledgeFeedback') as mock_crud_class:
            mock_crud_instance = MagicMock()
            mock_crud_instance.create.side_effect = Exception("Database error")
            mock_crud_class.return_value = mock_crud_instance

            response = client.post(
                "/api/v1/ai/feedback",
                json=feedback_data
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["feedback_id"] is None
        assert "Error" in data["message"]

    def test_ai_health_check_success(self, client: TestClient):
        """Test chequeo de salud de IA exitoso"""
        
        # El test client ya maneja la conexión de BD correctamente
        # Solo necesitamos mockear el servicio de IA
        with patch('backend.api.v1.endpoints.ai.get_ai_service') as mock_service:
            
            # Mock del servicio AI
            mock_ai_service = MagicMock()
            mock_ai_service.sql_agent = True
            mock_ai_service.llm = MagicMock()  # Simular que existe
            mock_service.return_value = mock_ai_service

            response = client.get("/api/v1/ai/health")

        assert response.status_code == 200
        data = response.json()
        assert data["sql_agent_status"] == "OK"
        assert data["openai_connection"] is True
        # La conexión de BD puede ser True o False en el entorno de testing
        assert "database_connection" in data
        assert "available_roles" in data

    def test_ai_health_check_with_errors(self, client: TestClient):
        """Test chequeo de salud de IA con errores"""
        
        with patch('backend.api.v1.endpoints.ai.get_ai_service') as mock_service:
            mock_service.side_effect = Exception("Service error")

            response = client.get("/api/v1/ai/health")

        assert response.status_code == 200
        data = response.json()
        assert "Error" in data["sql_agent_status"]
        assert data["openai_connection"] is False

    def test_query_examples(self, client: TestClient):
        """Test obtener ejemplos de consultas"""
        response = client.get("/api/v1/ai/examples")
        
        assert response.status_code == 200
        data = response.json()
        assert "examples" in data
        assert "cliente" in data["examples"]
        assert "tecnico" in data["examples"]
        assert "administrador" in data["examples"]
        assert len(data["examples"]["administrador"]) > 0

    def test_database_schema_info_admin_only(self, client: TestClient):
        """Test información de esquema solo para admin"""
        with patch('backend.api.v1.endpoints.ai.get_ai_service') as mock_service:
            mock_ai_service = MagicMock()
            mock_ai_service._get_database_schema_info.return_value = "Schema info mock"
            mock_ai_service.role_permissions = {
                "cliente": ["clients"],
                "tecnico": ["clients", "products"],
                "administrador": ["clients", "products", "orders"]
            }
            mock_service.return_value = mock_ai_service

            response = client.get("/api/v1/ai/schema?user_role=administrador")

        assert response.status_code == 200
        data = response.json()
        assert "schema_info" in data
        assert "available_tables_by_role" in data

    def test_database_schema_info_forbidden_for_non_admin(self, client: TestClient):
        """Test que no-admin no puede acceder a esquema"""
        response = client.get("/api/v1/ai/schema?user_role=cliente")
        
        assert response.status_code == 403
        data = response.json()
        assert "Solo los administradores" in data["detail"]

    def test_sql_query_invalid_role(self, client: TestClient):
        """Test consulta SQL con rol inválido"""
        response = client.post(
            "/api/v1/ai/sql-query",
            json={
                "query": "Test query",
                "user_role": "invalid_role",
                "user_id": None,
                "include_sql": True
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_sql_query_missing_query(self, client: TestClient):
        """Test consulta SQL sin query"""
        response = client.post(
            "/api/v1/ai/sql-query",
            json={
                "user_role": "administrador",
                "user_id": None,
                "include_sql": True
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_feedback_missing_required_fields(self, client: TestClient):
        """Test feedback sin campos requeridos"""
        response = client.post(
            "/api/v1/ai/feedback",
            json={
                "rating": 5
            }
        )
        
        assert response.status_code == 422  # Validation error 