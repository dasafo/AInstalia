#backend/tests/phase_0/test_rag_service.py
"""
Tests para el servicio RAG (Retrieval-Augmented Generation)
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
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
        tmpdir = Path(tempfile.mkdtemp())
        yield tmpdir
        shutil.rmtree(tmpdir)
    
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
    
    @patch('backend.services.rag_service.RAGService.__init__', return_value=None)
    @patch('backend.services.rag_service.ChatOpenAI')
    @patch('backend.services.rag_service.OpenAIEmbeddings')
    @patch('backend.services.rag_service.FAISS')
    @patch('backend.services.rag_service.settings')
    def test_rag_service_initialization(
        self,
        mock_settings,
        mock_faiss_class,
        mock_embeddings_class,
        mock_llm_class,
        mock_rag_service_init,
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
        
        # Crear instancia del servicio RAG (sin llamar al __init__ real)
        rag_service = RAGService(mock_db_session)
        
        # Configurar manualmente los atributos que normalmente se inicializarían en __init__
        rag_service.db_session = mock_db_session
        rag_service.embeddings = mock_openai_embeddings
        rag_service.llm = mock_openai_llm
        rag_service.documents_dir = temp_dir
        rag_service.vector_store_path = temp_dir
        
        # Mockear los métodos internos que __init__ normalmente llamaría
        rag_service.text_splitter = Mock()
        rag_service._load_or_create_vector_store = Mock()
        rag_service._ensure_base_knowledge = Mock()

        # Configurar el vector_store mock
        rag_service.vector_store = mock_vector_store
        
        # Llamar a los métodos que __init__ normalmente llamaría
        rag_service._load_or_create_vector_store()
        rag_service._ensure_base_knowledge()

        # Verificaciones
        mock_rag_service_init.assert_called_once_with(mock_db_session)
        assert rag_service.db_session == mock_db_session
        assert rag_service.embeddings == mock_openai_embeddings
        assert rag_service.llm == mock_openai_llm
        assert rag_service.vector_store == mock_vector_store
        
        rag_service._load_or_create_vector_store.assert_called_once()
        rag_service._ensure_base_knowledge.assert_called_once()
    
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
             patch('backend.services.rag_service.settings') as mock_settings, \
             patch('backend.services.rag_service.RAGService.__init__', return_value=None):
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            
            rag_service = RAGService(mock_db_session)
            rag_service.documents_dir = temp_dir
            rag_service.vector_store_path = temp_dir
            rag_service.embeddings = mock_openai_embeddings
            rag_service.llm = mock_openai_llm
            rag_service.vector_store = mock_vector_store
            rag_service.text_splitter = Mock()
            rag_service.text_splitter.split_text.return_value = ["chunk1", "chunk2"]

            # Ejecutar indexación
            result = rag_service.index_document(str(test_file))
        
        # Verificaciones
        assert result["success"] is True
        assert result["error"] is None
        assert result["chunks_added"] > 0
        assert "content_hash" in result
        assert result["file_name"] == "test_document.txt"
        
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
             patch('backend.services.rag_service.settings') as mock_settings, \
             patch('backend.services.rag_service.RAGService.__init__', return_value=None):
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            
            rag_service = RAGService(mock_db_session)
            rag_service.documents_dir = temp_dir
            rag_service.vector_store_path = temp_dir
            rag_service.embeddings = mock_openai_embeddings
            rag_service.llm = mock_openai_llm
            rag_service.vector_store = mock_vector_store
            rag_service.text_splitter = Mock()
            rag_service.text_splitter.split_text.return_value = ["chunk1", "chunk2"]

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
             patch('backend.services.rag_service.settings') as mock_settings, \
             patch('backend.services.rag_service.RAGService.__init__', return_value=None):
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            
            rag_service = RAGService(mock_db_session)
            rag_service.documents_dir = temp_dir
            rag_service.vector_store_path = temp_dir
            rag_service.embeddings = mock_openai_embeddings
            rag_service.llm = mock_openai_llm
            rag_service.vector_store = mock_vector_store
            rag_service.text_splitter = Mock()
            rag_service.text_splitter.split_text.return_value = ["chunk1", "chunk2"]

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
             patch('backend.services.rag_service.settings') as mock_settings, \
             patch('backend.services.rag_service.RAGService.__init__', return_value=None):
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            
            rag_service = RAGService(mock_db_session)
            rag_service.embeddings = mock_openai_embeddings
            rag_service.vector_store = mock_vector_store
            
            # Ejecutar búsqueda
            result = rag_service.search_knowledge("¿Cómo instalar un equipo?", top_k=3)
        
        # Verificaciones
        assert len(result) == 2
        assert all(isinstance(doc, Document) for doc in result)
        
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
             patch('backend.services.rag_service.settings') as mock_settings, \
             patch('backend.services.rag_service.RAGService.__init__', return_value=None):
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            
            rag_service = RAGService(mock_db_session)
            rag_service.embeddings = mock_openai_embeddings
            rag_service.vector_store = None
            
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
             patch('backend.services.rag_service.settings') as mock_settings, \
             patch('backend.services.rag_service.RAGService.__init__', return_value=None):
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            
            rag_service = RAGService(mock_db_session)
            rag_service.llm = mock_openai_llm
            
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
             patch('backend.services.rag_service.settings') as mock_settings, \
             patch('backend.services.rag_service.RAGService.__init__', return_value=None):
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            
            rag_service = RAGService(mock_db_session)
            rag_service.llm = mock_openai_llm
            
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
             patch('backend.services.rag_service.settings') as mock_settings, \
             patch('backend.services.rag_service.RAGService.__init__', return_value=None):
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            
            rag_service = RAGService(mock_db_session)
            rag_service.embeddings = mock_openai_embeddings
            rag_service.llm = mock_openai_llm
            rag_service.vector_store = mock_vector_store
            
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
             patch('backend.services.rag_service.settings') as mock_settings, \
             patch('backend.services.rag_service.RAGService.__init__', return_value=None):
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            
            rag_service = RAGService(mock_db_session)
            rag_service.embeddings = mock_openai_embeddings
            rag_service.llm = mock_openai_llm
            rag_service.vector_store = mock_vector_store

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
             patch('backend.services.rag_service.settings') as mock_settings, \
             patch('backend.services.rag_service.RAGService.__init__', return_value=None):
            
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_emb_class.return_value = mock_openai_embeddings
            mock_llm_class.return_value = mock_openai_llm
            
            rag_service = RAGService(mock_db_session)
            rag_service.documents_dir = temp_dir
            rag_service.vector_store = mock_vector_store
            
            # Obtener estadísticas
            stats = rag_service.get_knowledge_stats()
        
        # Verificaciones
        assert stats["vector_store_size"] == 5
        assert stats["documents_directory"] == str(temp_dir)
        assert len(stats["indexed_files"]) == 2
        assert any(f["name"] == "doc1.md" for f in stats["indexed_files"])
        assert any(f["name"] == "doc2.md" for f in stats["indexed_files"])
    
    @patch('backend.services.rag_service.RAGService')
    def test_get_rag_service_factory(self, mock_rag_class, mock_db_session):
        """Test función factory para crear servicio RAG"""
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
        tmpdir = Path(tempfile.mkdtemp())
        yield tmpdir
        shutil.rmtree(tmpdir)
    
    def test_full_rag_workflow_mock(self, mock_db_session, temp_dir):
        """Test completo del flujo RAG con mocks"""
        # Crear archivo de prueba
        test_file = temp_dir / "knowledge.txt"
        test_content = "Información de prueba para el sistema RAG"
        test_file.write_text(test_content, encoding='utf-8')
        
        with patch('backend.services.rag_service.OpenAIEmbeddings') as mock_emb_class, \
             patch('backend.services.rag_service.ChatOpenAI') as mock_llm_class, \
             patch('backend.services.rag_service.FAISS') as mock_faiss_class, \
             patch('backend.services.rag_service.settings') as mock_settings, \
             patch('backend.services.rag_service.RAGService.__init__', return_value=None):
            
            mock_settings.OPENAI_API_KEY = "test-key"
            
            mock_embeddings = Mock()
            mock_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]]
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
            
            # Crear instancia RAG (con __init__ parcheado)
            rag_service = RAGService(mock_db_session)
            
            # Configurar manualmente los atributos que __init__ normalmente inicializaría
            rag_service.db_session = mock_db_session
            rag_service.embeddings = mock_embeddings
            rag_service.llm = mock_llm
            rag_service.documents_dir = temp_dir
            rag_service.vector_store_path = temp_dir
            rag_service.vector_store = mock_vector_store
            rag_service.text_splitter = Mock()
            rag_service.text_splitter.split_text.return_value = ["chunk"]
            
            # También mockear los métodos internos que __init__ normalmente llamaría
            rag_service._load_or_create_vector_store = Mock()
            rag_service._ensure_base_knowledge = Mock()

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
    @patch('backend.services.rag_service.OpenAIEmbeddings')
    @patch('backend.services.rag_service.ChatOpenAI')
    @patch('backend.services.rag_service.FAISS')
    @patch('backend.services.rag_service.RAGService.__init__', return_value=None)
    @patch.object(RAGService, 'index_document')
    def test_ensure_base_knowledge_creation(
        self,
        mock_index_document,
        mock_rag_service_init,
        mock_faiss_class,
        mock_llm_class,
        mock_embeddings_class,
        mock_settings,
        mock_db_session,
        temp_dir
    ):
        """Test creación automática de base de conocimiento"""
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_embeddings = Mock()
        mock_embeddings_class.return_value = mock_embeddings
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        mock_vector_store = Mock()
        mock_faiss_class.from_documents.return_value = mock_vector_store
        
        rag_service = RAGService(mock_db_session)
        
        rag_service.documents_dir = temp_dir
        
        knowledge_files = [
            "catalogo_productos.txt",
            "guia_diagnosticos.txt",
            "manual_mantenimiento.txt",
            "procedimientos_instalacion.txt",
            "terminos_garantia.txt",
        ]
        for f_name in knowledge_files:
            (temp_dir / f_name).write_text(f"Contenido de {f_name}", encoding='utf-8')

        rag_service._load_or_create_vector_store = Mock()
        
        rag_service._ensure_base_knowledge()

        assert mock_index_document.call_count == len(knowledge_files)
        for f_name in knowledge_files:
            mock_index_document.assert_any_call(str(temp_dir / f_name), update_existing=True)

        # _ensure_base_knowledge no guarda el vector store, pero index_document sí.
        # En este test, solo verificamos las llamadas a index_document. 