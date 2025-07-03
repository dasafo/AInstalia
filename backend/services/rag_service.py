#backend/services/rag_service.py
"""
Servicio RAG (Retrieval-Augmented Generation) para AInstalia
Sistema de recuperación y generación aumentada para consultas de conocimiento
"""
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import numpy as np
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.knowledge_feedback_model import KnowledgeFeedback
from sqlalchemy.orm import Session

logger = get_logger("ainstalia.rag_service")

class RAGService:
    """Servicio de Retrieval-Augmented Generation para consultas de conocimiento"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.documents_dir = Path(__file__).parent.parent.parent / "knowledge_base"
        self.vector_store_path = Path(__file__).parent.parent.parent / "vector_store"
        
        # Inicializar componentes
        self.embeddings = self._initialize_embeddings()
        self.llm = self._initialize_llm()
        self.text_splitter = self._initialize_text_splitter()
        self.vector_store = None
        
        # Crear directorios si no existen
        self.documents_dir.mkdir(exist_ok=True)
        self.vector_store_path.mkdir(exist_ok=True)
        
        # Cargar o crear vector store
        self._load_or_create_vector_store()
        
        # Documentos de conocimiento base de AInstalia
        self._ensure_base_knowledge()
        
    def _initialize_embeddings(self) -> OpenAIEmbeddings:
        """Inicializa el modelo de embeddings"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no está configurada")
        
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Inicializa el modelo de lenguaje"""
        return ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def _initialize_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """Inicializa el divisor de texto"""
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""]
        )
    
    def _load_or_create_vector_store(self) -> None:
        """Carga el vector store existente o crea uno nuevo"""
        try:
            vector_store_file = self.vector_store_path / "faiss_index"
            
            if vector_store_file.exists():
                logger.info("Cargando vector store existente...")
                self.vector_store = FAISS.load_local(
                    str(self.vector_store_path), 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"Vector store cargado con {self.vector_store.index.ntotal} vectores")
            else:
                logger.info("Creando nuevo vector store...")
                # Crear vector store vacío
                initial_docs = [Document(page_content="AInstalia - Sistema de información inicial", metadata={"source": "init"})]
                self.vector_store = FAISS.from_documents(initial_docs, self.embeddings)
                self._save_vector_store()
                
        except Exception as e:
            logger.error(f"Error cargando vector store: {e}")
            # Crear vector store de emergencia
            initial_docs = [Document(page_content="AInstalia - Sistema de información", metadata={"source": "emergency"})]
            self.vector_store = FAISS.from_documents(initial_docs, self.embeddings)
    
    def _save_vector_store(self) -> None:
        """Guarda el vector store en disco"""
        try:
            self.vector_store.save_local(str(self.vector_store_path))
            logger.info("Vector store guardado exitosamente")
        except Exception as e:
            logger.error(f"Error guardando vector store: {e}")
    
    def _ensure_base_knowledge(self) -> None:
        """Asegura que existe conocimiento base de AInstalia"""
        base_knowledge_file = self.documents_dir / "ainstalia_knowledge_base.md"
        
        if not base_knowledge_file.exists():
            logger.info("Creando base de conocimiento inicial...")
            base_content = self._get_base_knowledge_content()
            
            with open(base_knowledge_file, 'w', encoding='utf-8') as f:
                f.write(base_content)
            
            # Indexar el conocimiento base
            self.index_document(str(base_knowledge_file), update_existing=True)
    
    def _get_base_knowledge_content(self) -> str:
        """Retorna el contenido base de conocimiento de AInstalia"""
        return """# Base de Conocimiento AInstalia

## Sobre AInstalia
AInstalia es una empresa especializada en mantenimiento industrial que ofrece servicios integrales de instalación, mantenimiento y reparación de equipos industriales.

## Servicios Principales

### Mantenimiento Preventivo
- Inspecciones regulares programadas
- Limpieza y lubricación de equipos
- Reemplazo de componentes según cronograma
- Calibración de instrumentos

### Mantenimiento Correctivo
- Reparaciones de emergencia
- Diagnóstico de fallas
- Reemplazo de piezas dañadas
- Restauración de funcionalidad

### Instalación de Equipos
- Instalación de sistemas HVAC
- Montaje de maquinaria industrial
- Conexiones eléctricas y de control
- Pruebas de puesta en marcha

## Productos y Equipos

### Aires Acondicionados
- Modelos: AC-100, AC-200, AC-300, AC-CENTRAL-500
- Capacidades: 12,000 a 60,000 BTU
- Eficiencia energética SEER 16-22
- Garantía: 2-5 años según modelo

### Bombas Industriales
- Tipos: Centrífugas, de desplazamiento positivo
- Materiales: Acero inoxidable, hierro fundido
- Aplicaciones: Agua, químicos, petróleo
- Presiones: 50-500 PSI

### Compresores
- Tipos: Tornillo, pistón, centrífugo
- Capacidades: 5-500 HP
- Aplicaciones industriales y comerciales
- Sistemas de control automático

### Motores Eléctricos
- Potencias: 0.5-200 HP
- Voltajes: 220V, 440V, 2300V
- Tipos: Inducción, síncronos
- Eficiencias Premium y Super Premium

## Procedimientos de Seguridad

### Antes del Trabajo
1. Evaluación de riesgos del sitio
2. Uso obligatorio de EPP
3. Verificación de herramientas
4. Comunicación con supervisor

### Durante el Trabajo
1. Seguir procedimientos establecidos
2. Documentar todas las actividades
3. Reportar cualquier anomalía
4. Mantener área de trabajo limpia

### Después del Trabajo
1. Pruebas de funcionamiento
2. Limpieza del área
3. Documentación completa
4. Entrega formal al cliente

## Códigos de Error Comunes

### Aires Acondicionados
- E1: Sensor de temperatura defectuoso
- E2: Problema en compresor
- E3: Baja presión de refrigerante
- E4: Filtro obstruido

### Bombas
- P1: Cavitación
- P2: Sobrecalentamiento
- P3: Vibración excesiva
- P4: Fuga en sellos

### Compresores
- C1: Sobrepresión
- C2: Temperatura alta
- C3: Falta de lubricación
- C4: Problema eléctrico

## Garantías y Políticas

### Términos de Garantía
- Equipos nuevos: 12-60 meses según tipo
- Reparaciones: 90 días
- Instalaciones: 12 meses
- Mantenimiento: 30 días

### Política de Respuesta
- Emergencias: 4 horas máximo
- Mantenimiento programado: 24-48 horas
- Instalaciones: Coordinado con cliente
- Soporte técnico: 24/7 disponible

## Contacto y Soporte
- Teléfono emergencias: 1-800-AINSTALIA
- Email técnico: soporte@ainstalia.com
- Portal web: www.ainstalia.com
- App móvil: AInstalia Mobile

## Última actualización
Documento actualizado el: """ + datetime.now().strftime("%Y-%m-%d") + """
Versión: 1.0
"""
    
    def index_document(self, file_path: str, update_existing: bool = False) -> Dict[str, Any]:
        """
        Indexa un documento en el vector store
        
        Args:
            file_path: Ruta del archivo a indexar
            update_existing: Si actualizar documentos existentes
            
        Returns:
            Dict con resultado de la indexación
        """
        try:
            logger.info(f"Indexando documento: {file_path}")
            
            # Verificar que el archivo existe
            if not Path(file_path).exists():
                return {
                    "success": False,
                    "error": f"Archivo no encontrado: {file_path}",
                    "chunks_added": 0
                }
            
            # Leer contenido del archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return {
                    "success": False,
                    "error": "Archivo vacío",
                    "chunks_added": 0
                }
            
            # Generar hash del contenido para evitar duplicados
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Dividir texto en chunks
            text_chunks = self.text_splitter.split_text(content)
            
            # Crear documentos con metadata
            documents = []
            for i, chunk in enumerate(text_chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": file_path,
                        "chunk_id": i,
                        "content_hash": content_hash,
                        "indexed_at": datetime.now().isoformat(),
                        "file_name": Path(file_path).name
                    }
                )
                documents.append(doc)
            
            # Agregar al vector store
            if documents:
                self.vector_store.add_documents(documents)
                self._save_vector_store()
                
                logger.info(f"Documento indexado exitosamente: {len(documents)} chunks")
                
                return {
                    "success": True,
                    "error": None,
                    "chunks_added": len(documents),
                    "content_hash": content_hash,
                    "file_name": Path(file_path).name
                }
            else:
                return {
                    "success": False,
                    "error": "No se pudieron crear chunks del documento",
                    "chunks_added": 0
                }
                
        except Exception as e:
            logger.error(f"Error indexando documento: {e}")
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "chunks_added": 0
            }
    
    def search_knowledge(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Busca conocimiento relevante en el vector store
        
        Args:
            query: Consulta de búsqueda
            top_k: Número de documentos más relevantes a retornar
            
        Returns:
            Lista de documentos relevantes
        """
        try:
            if not self.vector_store:
                logger.warning("Vector store no inicializado")
                return []
            
            # Realizar búsqueda de similitud
            relevant_docs = self.vector_store.similarity_search(
                query, 
                k=top_k
            )
            
            logger.info(f"Encontrados {len(relevant_docs)} documentos relevantes para: '{query}'")
            return relevant_docs
            
        except Exception as e:
            logger.error(f"Error en búsqueda de conocimiento: {e}")
            return []
    
    def generate_answer(
        self, 
        question: str, 
        context_docs: List[Document],
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Genera una respuesta usando RAG
        
        Args:
            question: Pregunta del usuario
            context_docs: Documentos de contexto relevantes
            include_sources: Si incluir fuentes en la respuesta
            
        Returns:
            Dict con respuesta generada y metadatos
        """
        try:
            if not context_docs:
                return {
                    "success": False,
                    "answer": "No se encontró información relevante para responder tu pregunta.",
                    "sources": [],
                    "confidence": 0.0,
                    "error": "Sin documentos de contexto"
                }
            
            # Preparar contexto
            context = "\n\n".join([doc.page_content for doc in context_docs])
            
            # Crear prompt para RAG
            rag_prompt = PromptTemplate(
                input_variables=["context", "question"],
                template="""
Eres un asistente experto en AInstalia, una empresa de mantenimiento industrial.

CONTEXTO RELEVANTE:
{context}

PREGUNTA DEL USUARIO: {question}

INSTRUCCIONES:
1. Usa SOLO la información del contexto proporcionado para responder
2. Si la información no está en el contexto, dilo claramente
3. Responde en español de forma clara y profesional
4. Incluye detalles técnicos cuando sea relevante
5. Si hay procedimientos, menciona los pasos importantes
6. Mantén un tono profesional pero amigable

RESPUESTA:
"""
            )
            
            # Generar respuesta
            formatted_prompt = rag_prompt.format(context=context, question=question)
            response = self.llm.invoke(formatted_prompt)
            
            # Extraer fuentes si se solicita
            sources = []
            if include_sources:
                sources = list(set([
                    doc.metadata.get("file_name", doc.metadata.get("source", "Desconocido"))
                    for doc in context_docs
                ]))
            
            # Calcular confianza basada en relevancia (simplificado)
            confidence = min(len(context_docs) / 5.0, 1.0)  # Máximo 1.0 con 5+ docs
            
            logger.info(f"Respuesta RAG generada para: '{question}' con confianza {confidence}")
            
            return {
                "success": True,
                "answer": response.content,
                "sources": sources,
                "confidence": confidence,
                "error": None,
                "docs_used": len(context_docs)
            }
            
        except Exception as e:
            logger.error(f"Error generando respuesta RAG: {e}")
            return {
                "success": False,
                "answer": None,
                "sources": [],
                "confidence": 0.0,
                "error": f"Error interno: {str(e)}"
            }
    
    async def query_knowledge(
        self,
        question: str,
        include_sources: bool = True,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Método principal para consultas de conocimiento
        
        Args:
            question: Pregunta del usuario
            include_sources: Si incluir fuentes
            top_k: Número de documentos relevantes a buscar
            
        Returns:
            Dict con respuesta completa
        """
        try:
            logger.info(f"Procesando consulta de conocimiento: '{question}'")
            
            # Buscar documentos relevantes
            relevant_docs = self.search_knowledge(question, top_k=top_k)
            
            # Generar respuesta
            result = self.generate_answer(
                question=question,
                context_docs=relevant_docs,
                include_sources=include_sources
            )
            
            # Agregar metadatos adicionales
            result.update({
                "query": question,
                "timestamp": datetime.now().isoformat(),
                "docs_searched": len(relevant_docs)
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error en consulta de conocimiento: {e}")
            return {
                "success": False,
                "answer": None,
                "sources": [],
                "confidence": 0.0,
                "error": f"Error interno: {str(e)}",
                "query": question,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de conocimiento"""
        try:
            stats = {
                "vector_store_size": self.vector_store.index.ntotal if self.vector_store else 0,
                "documents_directory": str(self.documents_dir),
                "indexed_files": [],
                "last_updated": None
            }
            
            # Contar archivos en el directorio de documentos
            if self.documents_dir.exists():
                for file_path in self.documents_dir.glob("*.md"):
                    stats["indexed_files"].append({
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                "error": f"Error obteniendo estadísticas: {str(e)}"
            }

# Factory function
def get_rag_service(db_session: Session) -> RAGService:
    """Factory function para crear instancia del servicio RAG"""
    return RAGService(db_session) 