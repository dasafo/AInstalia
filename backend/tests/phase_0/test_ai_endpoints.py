#backend/tests/phase_0/test_ai_endpoints.py
"""
Tests para los endpoints de AI
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import asyncio
import time

from backend.main import app
from backend.db.session import get_db
from backend.services.ai_service import get_ai_service
from backend.services.rag_service import get_rag_service
from backend.models.knowledge_feedback_model import KnowledgeFeedback
from langchain.docstore.document import Document
from backend.schemas.ai_schema import UserRole


class TestAIEndpoints:
    """Tests para endpoints de AI"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock de sesión de base de datos"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def mock_ai_service(self):
        """Mock del servicio AI"""
        mock_service = Mock()
        mock_service.generate_sql_query.return_value = {
            "success": True,
            "sql": "SELECT * FROM equipos WHERE tipo = 'Aire Acondicionado'",
            "error": None,
            "confidence": 0.95
        }
        mock_service.get_business_insights.return_value = {
            "success": True,
            "insights": ["Insight 1", "Insight 2"],
            "error": None
        }
        return mock_service
    
    @pytest.fixture
    def mock_rag_service(self):
        """Mock del servicio RAG"""
        mock_service = AsyncMock()
        mock_service.query_knowledge.return_value = {
            "success": True,
            "answer": "Para instalar un equipo, siga estos pasos...",
            "sources": ["manual_instalacion.txt", "procedimientos.txt"],
            "confidence": 0.9,
            "error": None,
            "query": "¿Cómo instalar un equipo?",
            "timestamp": datetime.now().isoformat(),
            "docs_searched": 5
        }
        mock_service.get_knowledge_stats.return_value = {
            "vector_store_size": 150,
            "documents_directory": "/docs/knowledge_base",
            "indexed_files": [
                {"name": "manual_instalacion.txt", "size": 1024, "modified": "2024-01-01"}
            ]
        }
        mock_service.index_all_documents.return_value = {
            "success": True,
            "total_documents": 5,
            "total_chunks": 45,
            "error": None
        }
        return mock_service
    
    @pytest.mark.asyncio
    @patch('backend.api.v1.endpoints.ai.get_ai_service')
    async def test_sql_query_endpoint_success(self, mock_get_ai_service, client, mock_db_session):
        """Test endpoint SQL query exitoso"""
        # Create mock AI service
        mock_ai_service = AsyncMock()
        mock_ai_service.execute_sql_query.return_value = {
            "success": True,
            "result": [{"count": 5}],
            "total_results": 1,
            "error": None,
            "sql_query": "SELECT COUNT(*) as count FROM clients",
            "user_role": "admin"
        }
        mock_get_ai_service.return_value = mock_ai_service
        
        # Override dependencies
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        request_data = {
            "query": "Mostrar todos los aires acondicionados",
            "user_role": "administrador"
        }
        
        response = client.post("/api/v1/ai/sql-query", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["result"] == [{"count": 5}]
        assert mock_ai_service.execute_sql_query.called
        
        # Verify service was called correctly
        mock_ai_service.execute_sql_query.assert_called_once_with(
            natural_query="Mostrar todos los aires acondicionados",
            user_role="administrador",
            user_id=None
        )
        
        # Cleanup
        app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    @patch('backend.api.v1.endpoints.ai.get_ai_service')
    async def test_sql_query_endpoint_error(self, mock_get_ai_service, client, mock_db_session):
        """Test endpoint SQL query con error"""
        # Create mock AI service
        mock_ai_service = AsyncMock()
        mock_ai_service.execute_sql_query.return_value = {
            "success": False,
            "result": None,
            "total_results": None,
            "error": "No se puede acceder a esa tabla",
            "sql_query": None,
            "user_role": "cliente"
        }
        mock_get_ai_service.return_value = mock_ai_service
        
        # Override dependencies
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        request_data = {
            "query": "Mostrar todos los aires acondicionados",
            "user_role": "cliente"
        }
        
        response = client.post("/api/v1/ai/sql-query", json=request_data)
        
        assert response.status_code == 200  # Success but with error in result
        data = response.json()
        assert data["success"] == False
        assert "No se puede acceder a esa tabla" in data["error"]
        
        # Cleanup
        app.dependency_overrides.clear()
    
    @patch('backend.api.v1.endpoints.ai.RAGService')
    def test_knowledge_query_endpoint_success(self, mock_rag_service_class, client, mock_db_session):
        """Test endpoint knowledge query exitoso"""
        # Configure the mock instance
        mock_rag_instance = AsyncMock()
        mock_rag_instance.query_knowledge.return_value = {
            "success": True,
            "answer": "Para instalar un equipo, siga estos pasos...",
            "sources": ["manual_instalacion.txt", "procedimientos.txt"],
            "confidence": 0.9,
            "error": None
        }
        mock_rag_service_class.return_value = mock_rag_instance
        
        # Override dependencies
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        request_data = {
            "query": "¿Cómo instalar un equipo?",
            "include_sources": True
        }
        
        response = client.post("/api/v1/ai/knowledge-query", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "Para instalar un equipo" in data["answer"]
        assert data["error"] is None
        assert len(data["sources"]) == 2
        assert "manual_instalacion.txt" in data["sources"]
        assert data["confidence"] == 0.9
        
        # Verificar que se llamó al servicio correctamente
        mock_rag_service_class.assert_called_once_with(mock_db_session)
        mock_rag_instance.query_knowledge.assert_called_once_with(
            query="¿Cómo instalar un equipo?",
            context=None
        )
        
        # Cleanup
        app.dependency_overrides.clear()
    
    @patch('backend.api.v1.endpoints.ai.RAGService')
    def test_knowledge_query_endpoint_error(self, mock_rag_service_class, client, mock_db_session):
        """Test endpoint knowledge query con error"""
        # Configure the mock instance for error
        mock_rag_instance = AsyncMock()
        mock_rag_instance.query_knowledge.return_value = {
            "success": False,
            "answer": None,
            "sources": [],
            "confidence": 0.0,
            "error": "Vector store no inicializado"
        }
        mock_rag_service_class.return_value = mock_rag_instance
        
        # Override dependencies
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        request_data = {
            "query": "¿Cómo instalar un equipo?",
            "include_sources": True
        }
        
        response = client.post("/api/v1/ai/knowledge-query", json=request_data)
        
        assert response.status_code == 200  # Success but with error in result
        data = response.json()
        assert data["success"] == False
        assert data["error"] == "Vector store no inicializado"
        
        # Cleanup
        app.dependency_overrides.clear()
    
    @patch('backend.api.v1.endpoints.ai.get_ai_service')
    def test_insights_endpoint_success(self, mock_get_ai_service, client, mock_db_session):
        """Test endpoint insights exitoso"""
        # Configure the mock AI service
        mock_ai_service = AsyncMock()
        mock_ai_service.get_business_insights.return_value = {
            "success": True,
            "insights": {
                "total_clients": 150,
                "monthly_revenue": 25000,
                "top_products": ["Aire Acondicionado XP-400", "Sistema de Climatización Pro"],
                "pending_orders": 12
            },
            "error": None
        }
        mock_get_ai_service.return_value = mock_ai_service
        
        # Override dependencies
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        response = client.get("/api/v1/ai/insights?user_role=administrador")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "total_clients" in data["insights"]
        assert data["insights"]["total_clients"] == 150
        assert data["user_role"] == "administrador"
        
        # Verificar que se llamó al servicio
        mock_get_ai_service.assert_called_once_with(mock_db_session)
        mock_ai_service.get_business_insights.assert_called_once_with(user_role="administrador")
        
        # Cleanup
        app.dependency_overrides.clear()
    
    @patch('backend.api.v1.endpoints.ai.CRUDKnowledgeFeedback')
    def test_feedback_endpoint_success(self, mock_crud_class, client, mock_db_session):
        """Test endpoint feedback exitoso"""
        # Configure the mock CRUD instance
        mock_crud_instance = Mock()
        mock_new_feedback = Mock()
        mock_new_feedback.id = 123  # Use integer instead of string
        mock_crud_instance.create.return_value = mock_new_feedback
        mock_crud_class.return_value = mock_crud_instance
        
        # Override dependencies
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        request_data = {
            "original_query": "¿Cómo funciona el sistema?",
            "ai_response": "El sistema funciona así...",
            "user_feedback": "Excelente respuesta",
            "rating": 5,
            "user_type": "administrador"
        }
        
        response = client.post("/api/v1/ai/feedback", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["feedback_id"] == 123  # Expect integer instead of string
        assert data["message"] == "Feedback recibido correctamente"
        
        # Verify mock was called
        mock_crud_class.assert_called_once()
        mock_crud_instance.create.assert_called_once()
        
        # Clean up
        app.dependency_overrides.clear()
    
    @patch('backend.api.v1.endpoints.ai.RAGService')
    def test_knowledge_stats_endpoint_success(self, mock_rag_service_class, client, mock_db_session):
        """Test endpoint knowledge stats exitoso"""
        # Configure the mock instance
        mock_rag_instance = AsyncMock()
        mock_rag_instance.get_knowledge_stats.return_value = {
            "vector_store_size": 150,
            "documents_directory": "/docs/knowledge_base",
            "indexed_files": [
                {"name": "manual_instalacion.txt", "size": 1024, "modified": "2024-01-01"}
            ]
        }
        mock_rag_service_class.return_value = mock_rag_instance
        
        # Override dependencies
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        response = client.get("/api/v1/ai/knowledge/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["stats"]["vector_store_size"] == 150
        assert "indexed_files" in data["stats"]
        
        # Verificar que se llamó al servicio
        mock_rag_service_class.assert_called_once_with(mock_db_session)
        mock_rag_instance.get_knowledge_stats.assert_called_once()
        
        # Cleanup
        app.dependency_overrides.clear()
    
    @patch('backend.api.v1.endpoints.ai.RAGService')
    def test_reindex_knowledge_endpoint_success(self, mock_rag_service_class, client, mock_db_session):
        """Test endpoint reindex knowledge exitoso"""
        # Configure the mock instance
        mock_rag_instance = AsyncMock()
        mock_rag_instance.index_documents.return_value = {
            "success": True,
            "indexed_documents": 5,
            "total_chunks": 45,
            "error": None
        }
        mock_rag_service_class.return_value = mock_rag_instance
        
        # Override dependencies
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        response = client.post("/api/v1/ai/knowledge/reindex")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["indexed_documents"] == 5
        assert data["total_chunks"] == 45
        
        # Verificar que se llamó al servicio
        mock_rag_service_class.assert_called_once_with(mock_db_session)
        mock_rag_instance.index_documents.assert_called_once()
        
        # Cleanup
        app.dependency_overrides.clear()
    
    @patch('backend.api.v1.endpoints.ai.RAGService')
    def test_reindex_knowledge_endpoint_error(self, mock_rag_service_class, client, mock_db_session):
        """Test endpoint reindex knowledge con error"""
        # Configure the mock instance for error
        mock_rag_instance = AsyncMock()
        mock_rag_instance.index_documents.return_value = {
            "success": False,
            "indexed_documents": 0,
            "total_chunks": 0,
            "error": "Error accediendo al directorio de documentos"
        }
        mock_rag_service_class.return_value = mock_rag_instance
        
        # Override dependencies
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        response = client.post("/api/v1/ai/knowledge/reindex")
        
        assert response.status_code == 500  # Internal server error
        data = response.json()
        
        assert "Error durante la re-indexación" in data["detail"]
        
        # Clean up
        app.dependency_overrides.clear()
    
    @patch('backend.api.v1.endpoints.ai.get_ai_service')
    def test_health_check_endpoint(self, mock_get_ai_service, client, mock_db_session):
        """Test endpoint health check"""
        # Configure the mock AI service
        mock_ai_service = Mock()
        mock_ai_service.sql_agent = True
        mock_ai_service.llm = True
        mock_get_ai_service.return_value = mock_ai_service
        
        # Configure database session to execute successfully
        mock_db_session.execute = Mock()
        
        # Override dependencies
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        response = client.get("/api/v1/ai/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["sql_agent_status"] == "OK"
        assert data["openai_connection"] is True
        assert data["database_connection"] is True
        assert "available_roles" in data
        assert len(data["available_roles"]) == 3
        
        # Cleanup
        app.dependency_overrides.clear()


class TestRAGIntegration:
    """Tests de integración para el sistema RAG"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_db_session(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def mock_ai_service(self):
        """Mock del servicio AI para tests de integración"""
        mock_service = Mock()
        mock_service.generate_sql_query.return_value = {
            "success": True,
            "sql": "SELECT * FROM equipos WHERE tipo = 'Aire Acondicionado'",
            "error": None,
            "confidence": 0.95
        }
        mock_service.get_business_insights.return_value = {
            "success": True,
            "insights": ["Insight 1", "Insight 2"],
            "error": None
        }
        return mock_service
    
    @patch('backend.api.v1.endpoints.ai.RAGService')
    def test_rag_workflow_integration(self, mock_rag_service_class, client, mock_db_session):
        """Test integración completa del flujo RAG"""
        # Mock RAG service
        mock_rag_service = AsyncMock()
        mock_rag_service_class.return_value = mock_rag_service
        
        # 1. Test obtener estadísticas
        mock_rag_service.get_knowledge_stats.return_value = {
            "vector_store_size": 0,
            "documents_directory": "/docs/knowledge_base",
            "indexed_files": []
        }
        
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        # Obtener estadísticas iniciales
        stats_response = client.get("/api/v1/ai/knowledge/stats")
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        assert stats_data["success"] is True
        assert stats_data["stats"]["vector_store_size"] == 0
        
        # 2. Test re-indexación
        mock_rag_service.index_documents.return_value = {
            "success": True,
            "indexed_documents": 5,
            "total_chunks": 50,
            "error": None
        }
        
        reindex_response = client.post("/api/v1/ai/knowledge/reindex")
        assert reindex_response.status_code == 200
        reindex_data = reindex_response.json()
        assert reindex_data["success"] is True
        
        # 3. Test consulta de conocimiento
        mock_rag_service.query_knowledge.return_value = {
            "success": True,
            "answer": "Respuesta de prueba",
            "sources": ["test.txt"],
            "confidence": 0.9,
            "error": None,
            "query": "pregunta de prueba",
            "timestamp": datetime.now().isoformat(),
            "docs_searched": 1
        }
        
        query_data = {
            "query": "pregunta de prueba",
            "include_sources": True
        }
        
        query_response = client.post("/api/v1/ai/knowledge-query", json=query_data)
        assert query_response.status_code == 200
        query_response_data = query_response.json()
        assert query_response_data["success"] is True
        assert query_response_data["answer"] == "Respuesta de prueba"
        
        # Clean up
        app.dependency_overrides.clear()
    
    @patch('backend.api.v1.endpoints.ai.RAGService')
    def test_rag_error_handling_integration(self, mock_rag_service_class, client, mock_db_session):
        """Test manejo de errores en integración RAG"""
        # Mock RAG service con errores
        mock_rag_service = AsyncMock()
        mock_rag_service_class.return_value = mock_rag_service
        
        # Test error en estadísticas
        mock_rag_service.get_knowledge_stats.side_effect = Exception("Error interno")
        
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        stats_response = client.get("/api/v1/ai/knowledge/stats")
        assert stats_response.status_code == 500
        
        # Test error en re-indexación
        mock_rag_service.get_knowledge_stats.side_effect = None  # Reset
        mock_rag_service.index_documents.return_value = {
            "success": False,
            "indexed_documents": 0,
            "total_chunks": 0,
            "error": "No se encontraron documentos para indexar"
        }
        
        reindex_response = client.post("/api/v1/ai/knowledge/reindex")
        assert reindex_response.status_code == 500
        
        # Test error en consulta
        mock_rag_service.query_knowledge.return_value = {
            "success": False,
            "answer": None,
            "sources": [],
            "confidence": 0.0,
            "error": "Vector store no inicializado",
            "query": "pregunta de prueba",
            "timestamp": datetime.now().isoformat(),
            "docs_searched": 0
        }
        
        query_data = {
            "query": "pregunta de prueba",
            "include_sources": True
        }
        
        query_response = client.post("/api/v1/ai/knowledge-query", json=query_data)
        assert query_response.status_code == 200  # Should return 200 with error in response
        query_data = query_response.json()
        assert query_data["success"] is False
        assert query_data["error"] == "Vector store no inicializado"
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_knowledge_query_validation(self, client, mock_db_session):
        """Test validación de entrada en knowledge query"""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        # Test sin pregunta
        response = client.post("/api/v1/ai/knowledge-query", json={})
        assert response.status_code == 422  # Validation error
        
        # Test pregunta vacía
        response = client.post("/api/v1/ai/knowledge-query", json={"query": ""})
        assert response.status_code == 422
        
        # Test pregunta muy larga
        very_long_question = "a" * 2000
        response = client.post("/api/v1/ai/knowledge-query", json={"query": very_long_question})
        assert response.status_code == 422
        
        # Cleanup
        app.dependency_overrides.clear()
    
    def test_sql_query_validation(self, client, mock_db_session, mock_ai_service):
        """Test validación de esquemas SQL query"""
        # Override dependencies
        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_ai_service] = lambda db: mock_ai_service
        
        # Test sin query
        response = client.post("/api/v1/ai/sql-query", json={"user_role": "administrador"})
        assert response.status_code == 422
        
        # Test sin user_role
        response = client.post("/api/v1/ai/sql-query", json={"query": "test"})
        assert response.status_code == 422
        
        # Test rol inválido
        response = client.post("/api/v1/ai/sql-query", json={
            "query": "test",
            "user_role": "invalid_role"
        })
        assert response.status_code == 422
        
        # Cleanup
        app.dependency_overrides.clear()
    
    def test_feedback_validation(self, client, mock_db_session):
        """Test validación de entrada en feedback"""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        # Test rating fuera de rango
        response = client.post("/api/v1/ai/feedback", json={
            "original_query": "test query",
            "ai_response": "test response",
            "user_feedback": "test feedback",
            "rating": 6,  # Máximo es 5
            "user_type": "administrador"
        })
        assert response.status_code == 422
        
        # Test rating negativo
        response = client.post("/api/v1/ai/feedback", json={
            "original_query": "test query",
            "ai_response": "test response",
            "user_feedback": "test feedback",
            "rating": -1,
            "user_type": "administrador"
        })
        assert response.status_code == 422
        
        # Test campos requeridos faltantes
        response = client.post("/api/v1/ai/feedback", json={
            "rating": 5
        })
        assert response.status_code == 422
        
        # Cleanup
        app.dependency_overrides.clear()


class TestRAGPerformance:
    """Tests de rendimiento para el sistema RAG"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_db_session(self):
        return Mock(spec=Session)
    
    @patch('backend.api.v1.endpoints.ai.RAGService')
    def test_concurrent_knowledge_queries(self, mock_rag_service_class, client, mock_db_session):
        """Test consultas concurrentes de conocimiento"""
        # Mock RAG service para respuestas rápidas
        mock_rag_service = AsyncMock()
        mock_rag_service_class.return_value = mock_rag_service
        
        mock_rag_service.query_knowledge.return_value = {
            "success": True,
            "answer": "Respuesta rápida",
            "sources": ["test.txt"],
            "confidence": 0.9,
            "error": None,
            "query": "pregunta de prueba",
            "timestamp": datetime.now().isoformat(),
            "docs_searched": 1
        }
        
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        # Realizar 5 consultas concurrentes
        async def make_concurrent_queries():
            tasks = []
            for i in range(5):
                query_data = {
                    "query": f"pregunta de prueba {i}",
                    "include_sources": True
                }
                task = asyncio.create_task(
                    asyncio.to_thread(
                        client.post, "/api/v1/ai/knowledge-query", json=query_data
                    )
                )
                tasks.append(task)
            
            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # Verificar que todas las respuestas fueron exitosas
            for response in responses:
                assert response.status_code == 200
                
            # Verificar que el tiempo total fue menor a 1 segundo (simulado)
            total_time = end_time - start_time
            assert total_time < 1.0  # Con mocks debería ser muy rápido
            
            return responses
        
        # Ejecutar test concurrente
        responses = asyncio.run(make_concurrent_queries())
        
        # Clean up dependency overrides
        app.dependency_overrides.clear()
    
    @patch('backend.api.v1.endpoints.ai.RAGService')
    def test_large_knowledge_base_stats(self, mock_rag_service_class, client, mock_db_session):
        """Test estadísticas con base de conocimiento grande"""
        # Mock RAG service con base de conocimiento simulada grande
        mock_rag_service = AsyncMock()
        mock_rag_service_class.return_value = mock_rag_service
        
        mock_rag_service.get_knowledge_stats.return_value = {
            "vector_store_size": 100,  # Simular 100 documentos
            "documents_directory": "/docs/knowledge_base",
            "indexed_files": [f"doc_{i}.txt" for i in range(100)]
        }
        
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        start_time = time.time()
        response = client.get("/api/v1/ai/knowledge/stats")
        end_time = time.time()
        
        # Verificar respuesta exitosa y rápida
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0  # Debería ser rápido con mocks
        
        # Verificar estructura de respuesta
        data = response.json()
        assert data["success"] is True
        assert data["stats"]["vector_store_size"] == 100
        assert len(data["stats"]["indexed_files"]) == 100
        
        # Clean up dependency overrides
        app.dependency_overrides.clear() 