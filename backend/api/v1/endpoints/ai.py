#backend/api/v1/endpoints/ai.py
"""
Endpoints para servicios de IA - Agente SQL y más
"""
import time
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.services.ai_service import get_ai_service, AIService
from backend.schemas.ai_schema import (
    SQLQueryRequest, SQLQueryResponse,
    KnowledgeQueryRequest, KnowledgeQueryResponse, FeedbackIn, 
    FeedbackOut, AIHealthResponse, UserRole
)
from pydantic import BaseModel, Field
from backend.core.logging import get_logger
from backend.models.knowledge_feedback_model import KnowledgeFeedback
from backend.services.rag_service import RAGService

logger = get_logger("ainstalia.ai_endpoints")

router = APIRouter()

@router.post("/sql-query", response_model=SQLQueryResponse)
async def execute_sql_query(
    request: SQLQueryRequest,
    db: AsyncSession = Depends(get_db)
) -> SQLQueryResponse:
    """
    Ejecuta consultas SQL en lenguaje natural usando IA
    
    - **query**: Consulta en lenguaje natural (ej: "¿Cuántos clientes tenemos?")
    - **user_role**: Rol del usuario (determina qué tablas puede acceder)
    - **user_id**: ID del usuario (para filtros personalizados)
    - **include_sql**: Si incluir la consulta SQL generada en la respuesta
    """
    try:
        start_time = time.time()
        
        logger.info(f"Nueva consulta SQL: '{request.query}' de rol: {request.user_role}")
        
        # Obtener servicio de IA
        ai_service = get_ai_service(db)
        
        # Ejecutar consulta
        result = await ai_service.execute_sql_query(
            natural_query=request.query,
            user_role=request.user_role.value,
            user_id=request.user_id
        )
        
        # Calcular tiempo de ejecución
        execution_time = (time.time() - start_time) * 1000
        
        # Preparar respuesta
        response_data = {
            "success": result["success"],
            "result": result["result"],
            "total_results": result.get("total_results"),
            "error": result["error"],
            "user_role": result.get("user_role"),
            "execution_time_ms": execution_time
        }
        
        # Incluir SQL solo si se solicita y es exitoso
        if request.include_sql and result["success"]:
            response_data["sql_query"] = result["sql_query"]
        
        return SQLQueryResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error en consulta SQL: {e}")
        execution_time = (time.time() - start_time) * 1000
        
        return SQLQueryResponse(
            success=False,
            error=f"Error interno: {str(e)}",
            result=None,
            total_results=None,
            sql_query=None,
            user_role=request.user_role.value,
            execution_time_ms=execution_time
        )

class BusinessInsightsRequest(BaseModel):
    query: str = Field(..., description="Tipo de insights solicitados")
    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Parámetros opcionales para refinar la consulta"
    )


class BusinessInsightsAPIResponse(BaseModel):
    success: bool
    insights: Optional[List[Any]] = None
    error: Optional[str] = None


@router.post("/insights", response_model=BusinessInsightsAPIResponse)
async def get_business_insights(
    request: BusinessInsightsRequest,
    user_role: UserRole = UserRole.administrador,
    db: AsyncSession = Depends(get_db)
) -> BusinessInsightsAPIResponse:
    """
    Obtiene insights automáticos del negocio usando el servicio IA.
    """
    if user_role != UserRole.administrador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a los insights completos"
        )

    try:
        ai_service = get_ai_service(db)
        service_response = await ai_service.get_business_insights({
            "query": request.query,
            "params": request.params or {},
            "user_role": user_role.value
        })
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error generando insights: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando insights: {str(exc)}"
        )

    if not isinstance(service_response, dict) or "success" not in service_response:
        logger.error("Contrato inválido del servicio de insights: falta el campo 'success'")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Contrato inválido del servicio de insights"
        )

    if service_response["success"]:
        insights_payload = service_response.get("insights") or []
        if not isinstance(insights_payload, list):
            insights_payload = [insights_payload]
        return BusinessInsightsAPIResponse(success=True, insights=insights_payload)

    error_message = service_response.get("error") or "No se pudo generar la información solicitada"
    logger.warning(f"Servicio de insights devolvió error controlado: {error_message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=BusinessInsightsAPIResponse(success=False, error=error_message).model_dump()
    )

@router.post("/knowledge-query", response_model=KnowledgeQueryResponse)
async def query_knowledge_base(
    request: KnowledgeQueryRequest,
    db: AsyncSession = Depends(get_db)
) -> KnowledgeQueryResponse:
    """
    Consulta la base de conocimiento usando RAG (Retrieval-Augmented Generation)
    
    - **query**: Pregunta sobre documentación técnica o procedimientos
    - **context**: Contexto adicional para mejorar la respuesta
    - **include_sources**: Si incluir las fuentes de información utilizadas
    """
    logger = get_logger()
    
    try:
        logger.info(f"Consulta de conocimiento RAG: '{request.query}'")
        
        # Crear instancia del servicio RAG
        rag_service = RAGService(db)
        
        # Realizar la consulta al sistema RAG
        result = await rag_service.query_knowledge(
            query=request.query,
            context=request.context
        )
        
        if result["success"]:
            return KnowledgeQueryResponse(
                success=True,
                answer=result["answer"],
                sources=result["sources"] if request.include_sources else None,
                confidence=result["confidence"],
                error=None
            )
        else:
            logger.warning(f"Consulta RAG falló: {result.get('error', 'Error desconocido')}")
            return KnowledgeQueryResponse(
                success=False,
                answer=None,
                sources=None,
                confidence=None,
                error=result.get("error", "Error procesando la consulta")
            )
        
    except Exception as e:
        logger.error(f"Error en consulta de conocimiento: {e}")
        return KnowledgeQueryResponse(
            success=False,
            error=f"Error interno: {str(e)}",
            answer=None,
            sources=None,
            confidence=None
        )

@router.post("/feedback", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback: FeedbackIn,
    db: AsyncSession = Depends(get_db)
) -> FeedbackOut:
    """Registra feedback del usuario sobre respuestas de IA."""
    logger = get_logger()
    logger.info(
        "Recibiendo feedback: usuario_tipo=%s, rating=%s",
        feedback.user_type,
        feedback.rating,
    )

    record = KnowledgeFeedback(
        question=feedback.original_query,
        expected_answer=feedback.ai_response,
        user_comment=feedback.user_comment,
        rating=feedback.rating,
        user_type=feedback.user_type.value if isinstance(feedback.user_type, UserRole) else feedback.user_type,
        status="pendiente",
    )

    try:
        db.add(record)
        await db.commit()
        await db.refresh(record)
    except Exception as exc:
        await db.rollback()
        logger.error("Error al procesar feedback: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo guardar el feedback",
        )

    return FeedbackOut.model_validate(record)

@router.get("/health", response_model=AIHealthResponse)
async def check_ai_health(
    db: AsyncSession = Depends(get_db)
) -> AIHealthResponse:
    """
    Verifica el estado de salud de los servicios de IA
    
    Retorna información sobre:
    - Estado del agente SQL
    - Conexión con OpenAI
    - Conexión con la base de datos
    - Roles disponibles
    """
    try:
        logger.info("Verificando estado de salud de servicios IA")
        
        # Verificar conexión con la base de datos
        try:
            await db.execute("SELECT 1")
            db_connection = True
        except:
            db_connection = False
        
        # Verificar servicio de IA
        try:
            ai_service = get_ai_service(db)
            sql_agent_status = "OK" if ai_service.sql_agent else "Error"
            openai_connection = ai_service.llm is not None
        except Exception as e:
            sql_agent_status = f"Error: {str(e)}"
            openai_connection = False
        
        return AIHealthResponse(
            sql_agent_status=sql_agent_status,
            openai_connection=openai_connection,
            database_connection=db_connection,
            available_roles=["cliente", "tecnico", "administrador"],
            last_check=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error verificando salud de IA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verificando estado: {str(e)}"
        )

@router.get("/examples")
async def get_query_examples():
    """
    Retorna ejemplos de consultas que se pueden hacer al agente SQL
    según el rol del usuario
    """
    examples = {
        "cliente": [
            "¿Cuántas órdenes he realizado este mes?",
            "¿Qué equipos tengo instalados?",
            "¿Cuándo vence mi contrato de mantenimiento?",
            "¿Qué mensajes tengo en mis chats recientes?",
            "¿Cuál es el estado de mi última orden?"
        ],
        "tecnico": [
            "¿Qué intervenciones tengo programadas para hoy?",
            "¿Cuántos equipos instalé este mes?",
            "¿Qué productos están en stock bajo en el almacén?",
            "¿Cuáles son mis últimas 10 intervenciones?",
            "¿Qué órdenes están pendientes de instalación?"
        ],
        "administrador": [
            "¿Cuántos clientes tenemos en total?",
            "¿Cuáles son los productos más vendidos?",
            "¿Qué técnicos han hecho más intervenciones?",
            "¿Cuántas órdenes están pendientes?",
            "¿Qué contratos vencen este mes?",
            "¿Cuánto stock tenemos por almacén?",
            "¿Cuál es el estado general del inventario?"
        ]
    }
    
    return {
        "message": "Ejemplos de consultas por rol de usuario",
        "examples": examples,
        "note": "Estas son consultas de ejemplo. Puedes hacer preguntas similares en lenguaje natural."
    }

@router.get("/schema")
async def get_database_schema_info(
    user_role: UserRole = UserRole.administrador,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna información del schema de la base de datos según el rol del usuario
    
    Solo disponible para administradores por seguridad
    """
    if user_role != UserRole.administrador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a la información del schema"
        )
    
    try:
        ai_service = get_ai_service(db)
        schema_info = await ai_service._get_database_schema_info()

        return {
            "success": True,
            "schema": schema_info,
            "available_tables_by_role": ai_service.role_permissions
        }

    except Exception as e:
        logger.error(f"Error obteniendo schema: {e}")
        return {
            "success": False,
            "error": f"Error obteniendo información del schema: {str(e)}"
        }

@router.get("/knowledge/stats")
async def get_knowledge_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene estadísticas de la base de conocimiento
    
    Retorna información sobre:
    - Número total de documentos indexados
    - Número de fragmentos de texto
    - Estado del vector store
    """
    try:
        logger.info("Obteniendo estadísticas de la base de conocimiento")

        rag_service = RAGService(db)
        stats = await rag_service.get_knowledge_stats()

        return stats

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de conocimiento: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/knowledge/index")
async def index_knowledge_base(
    db: AsyncSession = Depends(get_db)
):
    """
    Indexa documentos de la base de conocimiento
    
    **NOTA**: Esta operación puede tomar varios minutos dependiendo del tamaño
    de la base de conocimiento.
    """
    try:
        logger.info("Iniciando re-indexación de la base de conocimiento")

        rag_service = RAGService(db)
        return await rag_service.index_documents()

    except Exception as e:
        logger.error(f"Error re-indexando base de conocimiento: {e}")
        return {
            "success": False,
            "error": str(e)
        }
