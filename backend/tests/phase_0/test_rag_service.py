#backend/tests/phase_0/test_rag_service.py
"""
Tests para el servicio RAG (Retrieval-Augmented Generation)
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from backend.services.rag_service import RAGService, get_rag_service
from langchain.docstore.document import Document


class TestRAGService:
    """Tests para el servicio RAG"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock de sesión de base de datos"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def temp_dir(self):
        """Directorio temporal para tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_openai_embeddings(self):
        """Mock de OpenAI Embeddings"""
        mock_embeddings = Mock()
        mock_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]] * 10
        mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        return mock_embeddings
    
    @pytest.fixture
    def mock_openai_llm(self):
        """Mock de OpenAI LLM"""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Esta es una respuesta generada por el LLM"
        mock_llm.invoke.return_value = mock_response
        return mock_llm
    
    @pytest.fixture
    def mock_vector_store(self):
        """Mock de FAISS vector store"""
        mock_vs = Mock()
        mock_vs.index.ntotal = 5
        
        # Mock documents para similarity search
        mock_docs = [
            Document(
                page_content="Información sobre instalación de equipos",
                metadata={"source": "test_doc.txt", "chunk_id": 0}
            ),
            Document(
                page_content="Procedimientos de mantenimiento preventivo",
                metadata={"source": "test_doc.txt", "chunk_id": 1}
            )
        ]
        mock_vs.similarity_search.return_value = mock_docs
        mock_vs.add_documents.return_value = None
        mock_vs.save_local.return_value = None
        
        return mock_vs
    
    @patch('backend.services.rag_service.settings')
    @patch('backend.services.rag_service.FAISS')
    @patch('backend.services.rag_service.ChatOpenAI')
    @patch('backend.services.rag_service.OpenAIEmbeddings')
    def test_rag_service_initialization(
        self, 
        mock_embeddings_class,
        mock_llm_class,
        mock_faiss_class,
        mock_settings,
        mock_db_session,
        temp_dir,
        mock_openai_embeddings,
        mock_openai_llm,
        mock_vector_store
    ):
        """Test inicialización del servicio RAG"""
        # Setup mocks
        mock_settings.OPENAI_API_KEY = "test-api-key"
        mock_embeddings_class.return_value = mock_openai_embeddings
        mock_llm_class.return_value = mock_openai_llm
        mock_faiss_class.from_documents.return_value = mock_vector_store
        
        # Patch paths to use temp directory
        with patch.object(Path, '__new__', side_effect=lambda cls, *args: temp_dir / "test_path"):
            rag_service = RAGService(mock_db_session)
        
        # Verificaciones
        assert rag_service.db_session == mock_db_session
        assert rag_service.embeddings == mock_openai_embeddings
        assert rag_service.llm == mock_openai_llm
        assert rag_service.vector_store == mock_vector_store
        
        # Verificar que se llamaron los métodos de inicialización
        mock_embeddings_class.assert_called_once()
        mock_llm_class.assert_called_once()
    
    @patch('backend.services.rag_service.settings')
    def test_rag_service_initialization_without_api_key(self, mock_settings, mock_db_session):
        """Test que falla si no hay API key"""
        mock_settings.OPENAI_API_KEY = None
        
        with pytest.raises(ValueError, match="OPENAI_API_KEY no está configurada"):
            RAGService(mock_db_session)
    
    def test_index_document_success(
        self, 
        mock_db_session,
        temp_dir,
        mock_openai_embeddings,
        mock_openai_llm,
        mock_vector_store
    ):
        """Test indexación exitosa de documento"""
        # Crear archivo de prueba
        test_file = temp_dir / "test_document.txt"
        test_content = """
        # Manual de Instalación
        
        ## Paso 1: Preparación
        Verificar herramientas necesarias.
        
        ## Paso 2: Instalación
        Seguir procedimientos de seguridad.
        """
        test_file.write_text(test_content, encoding='utf-8')
        
        # Setup RAG service con mocks
        with patch('backend.services.rag_service.OpenAIEmbeddings') as mock_emb_class, \
             patch('backend.services.rag_service.ChatOpenAI') as mock_llm_class, \
             patch('backend.services.rag_service.FAISS') as mock_faiss_class, \
             patch('backend.services.rag_service.settings') as mock_settings:
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            mock_faiss_class.from_documents.return_value = mock_vector_store
            
            rag_service = RAGService(mock_db_session)
            rag_service.documents_dir = temp_dir
            
            # Ejecutar indexación
            result = rag_service.index_document(str(test_file))
        
        # Verificaciones
        assert result["success"] is True
        assert result["error"] is None
        assert result["chunks_added"] > 0
        assert "content_hash" in result
        assert result["file_name"] == "test_document.txt"
        
        # Verificar que se llamó add_documents
        mock_vector_store.add_documents.assert_called_once()
    
    def test_index_document_file_not_found(
        self, 
        mock_db_session,
        temp_dir,
        mock_openai_embeddings,
        mock_openai_llm,
        mock_vector_store
    ):
        """Test indexación de archivo inexistente"""
        with patch('backend.services.rag_service.OpenAIEmbeddings') as mock_emb_class, \
             patch('backend.services.rag_service.ChatOpenAI') as mock_llm_class, \
             patch('backend.services.rag_service.FAISS') as mock_faiss_class, \
             patch('backend.services.rag_service.settings') as mock_settings:
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            mock_faiss_class.from_documents.return_value = mock_vector_store
            
            rag_service = RAGService(mock_db_session)
            
            # Intentar indexar archivo inexistente
            result = rag_service.index_document("/path/to/nonexistent/file.txt")
        
        # Verificaciones
        assert result["success"] is False
        assert "Archivo no encontrado" in result["error"]
        assert result["chunks_added"] == 0
    
    def test_index_document_empty_file(
        self, 
        mock_db_session,
        temp_dir,
        mock_openai_embeddings,
        mock_openai_llm,
        mock_vector_store
    ):
        """Test indexación de archivo vacío"""
        # Crear archivo vacío
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("", encoding='utf-8')
        
        with patch('backend.services.rag_service.OpenAIEmbeddings') as mock_emb_class, \
             patch('backend.services.rag_service.ChatOpenAI') as mock_llm_class, \
             patch('backend.services.rag_service.FAISS') as mock_faiss_class, \
             patch('backend.services.rag_service.settings') as mock_settings:
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            mock_faiss_class.from_documents.return_value = mock_vector_store
            
            rag_service = RAGService(mock_db_session)
            
            # Intentar indexar archivo vacío
            result = rag_service.index_document(str(empty_file))
        
        # Verificaciones
        assert result["success"] is False
        assert "Archivo vacío" in result["error"]
        assert result["chunks_added"] == 0
    
    def test_search_knowledge_success(
        self,
        mock_db_session,
        mock_openai_embeddings,
        mock_openai_llm,
        mock_vector_store
    ):
        """Test búsqueda exitosa de conocimiento"""
        with patch('backend.services.rag_service.OpenAIEmbeddings') as mock_emb_class, \
             patch('backend.services.rag_service.ChatOpenAI') as mock_llm_class, \
             patch('backend.services.rag_service.FAISS') as mock_faiss_class, \
             patch('backend.services.rag_service.settings') as mock_settings:
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            mock_faiss_class.from_documents.return_value = mock_vector_store
            
            rag_service = RAGService(mock_db_session)
            
            # Ejecutar búsqueda
            result = rag_service.search_knowledge("¿Cómo instalar un equipo?", top_k=3)
        
        # Verificaciones
        assert len(result) == 2  # mock_vector_store devuelve 2 documentos
        assert all(isinstance(doc, Document) for doc in result)
        
        # Verificar que se llamó similarity_search con parámetros correctos
        mock_vector_store.similarity_search.assert_called_once_with(
            "¿Cómo instalar un equipo?", 
            k=3
        )
    
    def test_search_knowledge_no_vector_store(
        self,
        mock_db_session,
        mock_openai_embeddings,
        mock_openai_llm
    ):
        """Test búsqueda sin vector store inicializado"""
        # Configurar embeddings para devolver embedding individual
        mock_openai_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        
        with patch('backend.services.rag_service.OpenAIEmbeddings') as mock_emb_class, \
             patch('backend.services.rag_service.ChatOpenAI') as mock_llm_class, \
             patch('backend.services.rag_service.FAISS') as mock_faiss_class, \
             patch('backend.services.rag_service.settings') as mock_settings:
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            
            # Mock FAISS para que falle al cargar y crear vector store básico
            mock_vector_store = Mock()
            mock_vector_store.similarity_search.return_value = []
            mock_faiss_class.from_documents.return_value = mock_vector_store
            mock_faiss_class.load_local.side_effect = Exception("No existe vector store")
            
            rag_service = RAGService(mock_db_session)
            rag_service.vector_store = None  # Simular vector store no inicializado
            
            # Ejecutar búsqueda
            result = rag_service.search_knowledge("test query")
        
        # Verificar que retorna lista vacía cuando no hay vector store
        assert result == []
    
    def test_generate_answer_success(
        self,
        mock_db_session,
        mock_openai_embeddings,
        mock_openai_llm,
        mock_vector_store
    ):
        """Test generación exitosa de respuesta"""
        # Documentos de contexto mock
        context_docs = [
            Document(
                page_content="Los equipos se instalan siguiendo protocolos de seguridad",
                metadata={"file_name": "manual_instalacion.txt"}
            ),
            Document(
                page_content="Se requieren herramientas específicas para la instalación",
                metadata={"file_name": "procedimientos.txt"}
            )
        ]
        
        with patch('backend.services.rag_service.OpenAIEmbeddings') as mock_emb_class, \
             patch('backend.services.rag_service.ChatOpenAI') as mock_llm_class, \
             patch('backend.services.rag_service.FAISS') as mock_faiss_class, \
             patch('backend.services.rag_service.settings') as mock_settings:
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            mock_faiss_class.from_documents.return_value = mock_vector_store
            
            rag_service = RAGService(mock_db_session)
            
            # Ejecutar generación de respuesta
            result = rag_service.generate_answer(
                question="¿Cómo instalar un equipo?",
                context_docs=context_docs,
                include_sources=True
            )
        
        # Verificaciones
        assert result["success"] is True
        assert result["answer"] == "Esta es una respuesta generada por el LLM"
        assert result["error"] is None
        assert len(result["sources"]) == 2
        assert "manual_instalacion.txt" in result["sources"]
        assert "procedimientos.txt" in result["sources"]
        assert 0 < result["confidence"] <= 1
        assert result["docs_used"] == 2
        
        # Verificar que se llamó al LLM
        mock_openai_llm.invoke.assert_called_once()
    
    def test_generate_answer_no_context(
        self,
        mock_db_session,
        mock_openai_embeddings,
        mock_openai_llm,
        mock_vector_store
    ):
        """Test generación de respuesta sin contexto"""
        with patch('backend.services.rag_service.OpenAIEmbeddings') as mock_emb_class, \
             patch('backend.services.rag_service.ChatOpenAI') as mock_llm_class, \
             patch('backend.services.rag_service.FAISS') as mock_faiss_class, \
             patch('backend.services.rag_service.settings') as mock_settings:
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            mock_faiss_class.from_documents.return_value = mock_vector_store
            
            rag_service = RAGService(mock_db_session)
            
            # Ejecutar generación sin contexto
            result = rag_service.generate_answer(
                question="¿Cómo instalar un equipo?",
                context_docs=[],
                include_sources=True
            )
        
        # Verificaciones
        assert result["success"] is False
        assert "No se encontró información relevante" in result["answer"]
        assert result["sources"] == []
        assert result["confidence"] == 0.0
        assert "Sin documentos de contexto" in result["error"]
    
    @pytest.mark.asyncio
    async def test_query_knowledge_success(
        self,
        mock_db_session,
        mock_openai_embeddings,
        mock_openai_llm,
        mock_vector_store
    ):
        """Test consulta completa de conocimiento exitosa"""
        with patch('backend.services.rag_service.OpenAIEmbeddings') as mock_emb_class, \
             patch('backend.services.rag_service.ChatOpenAI') as mock_llm_class, \
             patch('backend.services.rag_service.FAISS') as mock_faiss_class, \
             patch('backend.services.rag_service.settings') as mock_settings:
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            mock_faiss_class.from_documents.return_value = mock_vector_store
            
            rag_service = RAGService(mock_db_session)
            
            # Ejecutar consulta completa
            result = await rag_service.query_knowledge(
                question="¿Cómo realizar mantenimiento?",
                include_sources=True,
                top_k=3
            )
        
        # Verificaciones
        assert result["success"] is True
        assert result["answer"] == "Esta es una respuesta generada por el LLM"
        assert result["error"] is None
        assert len(result["sources"]) > 0
        assert result["query"] == "¿Cómo realizar mantenimiento?"
        assert "timestamp" in result
        assert result["docs_searched"] == 2
        
        # Verificar que se llamaron los métodos internos
        mock_vector_store.similarity_search.assert_called_once()
        mock_openai_llm.invoke.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_knowledge_error_handling(
        self,
        mock_db_session,
        mock_openai_embeddings,
        mock_openai_llm,
        mock_vector_store
    ):
        """Test manejo de errores en query_knowledge"""
        # Configurar embeddings correctamente
        mock_openai_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        
        with patch('backend.services.rag_service.OpenAIEmbeddings') as mock_emb_class, \
             patch('backend.services.rag_service.ChatOpenAI') as mock_llm_class, \
             patch('backend.services.rag_service.FAISS') as mock_faiss_class, \
             patch('backend.services.rag_service.settings') as mock_settings:
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            mock_faiss_class.from_documents.return_value = mock_vector_store
            
            rag_service = RAGService(mock_db_session)
            
            # Simular error en search_knowledge
            with patch.object(rag_service, 'search_knowledge', side_effect=Exception("Error de prueba")):
                result = await rag_service.query_knowledge("pregunta de prueba")
        
        # Verificaciones - el error debe estar en el campo error, no en answer
        assert result["success"] is False
        assert result["answer"] is None
        assert "Error interno" in result["error"]
        assert result["sources"] == []
        assert result["confidence"] == 0.0
    
    def test_get_knowledge_stats(
        self,
        mock_db_session,
        temp_dir,
        mock_openai_embeddings,
        mock_openai_llm,
        mock_vector_store
    ):
        """Test obtención de estadísticas del sistema"""
        # Crear algunos archivos de prueba
        (temp_dir / "doc1.md").write_text("Contenido 1")
        (temp_dir / "doc2.md").write_text("Contenido 2")
        
        with patch('backend.services.rag_service.OpenAIEmbeddings') as mock_emb_class, \
             patch('backend.services.rag_service.ChatOpenAI') as mock_llm_class, \
             patch('backend.services.rag_service.FAISS') as mock_faiss_class, \
             patch('backend.services.rag_service.settings') as mock_settings:
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            mock_faiss_class.from_documents.return_value = mock_vector_store
            
            rag_service = RAGService(mock_db_session)
            rag_service.documents_dir = temp_dir
            
            # Obtener estadísticas
            stats = rag_service.get_knowledge_stats()
        
        # Verificaciones
        assert stats["vector_store_size"] == 5  # mock_vector_store.index.ntotal
        assert stats["documents_directory"] == str(temp_dir)
        assert len(stats["indexed_files"]) == 2
        assert any(f["name"] == "doc1.md" for f in stats["indexed_files"])
        assert any(f["name"] == "doc2.md" for f in stats["indexed_files"])
    
    def test_get_rag_service_factory(self, mock_db_session):
        """Test función factory para crear servicio RAG"""
        with patch('backend.services.rag_service.RAGService') as mock_rag_class:
            mock_instance = Mock()
            mock_rag_class.return_value = mock_instance
            
            result = get_rag_service(mock_db_session)
            
            mock_rag_class.assert_called_once_with(mock_db_session)
            assert result == mock_instance


class TestRAGServiceIntegration:
    """Tests de integración para el servicio RAG"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock de sesión de base de datos"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def temp_dir(self):
        """Directorio temporal para tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_full_rag_workflow_mock(self, mock_db_session, temp_dir):
        """Test completo del flujo RAG con mocks"""
        # Crear archivo de prueba
        test_file = temp_dir / "knowledge.txt"
        test_content = "Información de prueba para el sistema RAG"
        test_file.write_text(test_content, encoding='utf-8')
        
        with patch('backend.services.rag_service.OpenAIEmbeddings') as mock_emb_class, \
             patch('backend.services.rag_service.ChatOpenAI') as mock_llm_class, \
             patch('backend.services.rag_service.FAISS') as mock_faiss_class, \
             patch('backend.services.rag_service.settings') as mock_settings:
            
            # Setup mocks
            mock_settings.OPENAI_API_KEY = "test-key"
            
            mock_embeddings = Mock()
            mock_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]]  # Corregir longitud
            mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
            mock_emb_class.return_value = mock_embeddings
            
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Respuesta generada"
            mock_llm.invoke.return_value = mock_response
            mock_llm_class.return_value = mock_llm
            
            mock_vector_store = Mock()
            mock_vector_store.index.ntotal = 1
            mock_vector_store.similarity_search.return_value = [
                Document(page_content=test_content, metadata={"source": str(test_file)})
            ]
            mock_faiss_class.from_documents.return_value = mock_vector_store
            mock_faiss_class.load_local.side_effect = Exception("No existe")
            
            # Crear instancia RAG
            rag_service = RAGService(mock_db_session)
            rag_service.documents_dir = temp_dir
            
            # 1. Test indexación
            result = rag_service.index_document(str(test_file))
            assert result["success"] is True
            
            # 2. Test búsqueda
            docs = rag_service.search_knowledge("prueba")
            assert len(docs) > 0
            
            # 3. Test generación de respuesta
            answer = rag_service.generate_answer("pregunta", docs)
            assert answer["success"] is True
            assert answer["answer"] == "Respuesta generada"
    
    @patch('backend.services.rag_service.settings')
    def test_ensure_base_knowledge_creation(
        self, 
        mock_settings, 
        mock_db_session, 
        temp_dir
    ):
        """Test creación automática de base de conocimiento"""
        mock_settings.OPENAI_API_KEY = "test-key"
        
        with patch('backend.services.rag_service.OpenAIEmbeddings'), \
             patch('backend.services.rag_service.ChatOpenAI'), \
             patch('backend.services.rag_service.FAISS') as mock_faiss_class:
            
            mock_vector_store = Mock()
            mock_faiss_class.from_documents.return_value = mock_vector_store
            
            # Crear servicio RAG
            rag_service = RAGService(mock_db_session)
            rag_service.documents_dir = temp_dir
            
            # Ejecutar creación de base de conocimiento
            rag_service._ensure_base_knowledge()
            
            # Verificar que se creó el archivo
            base_file = temp_dir / "ainstalia_knowledge_base.md"
            assert base_file.exists()
            
            content = base_file.read_text(encoding='utf-8')
            assert "AInstalia" in content
            assert "Mantenimiento Preventivo" in content
            assert "Aires Acondicionados" in content 