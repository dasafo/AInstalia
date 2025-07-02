#backend/api/v1/endpoints/ai.py
"""
Endpoints para servicios de IA - Agente SQL y más
"""
import time
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.services.ai_service import get_ai_service, AIService
from backend.schemas.ai_schema import (
    SQLQueryRequest, SQLQueryResponse, BusinessInsightsResponse,
    KnowledgeQueryRequest, KnowledgeQueryResponse, FeedbackRequest, 
    FeedbackResponse, AIHealthResponse, UserRole
)
from backend.core.logging import get_logger
from backend.crud.knowledge_feedback_crud import CRUDKnowledgeFeedback

logger = get_logger("ainstalia.ai_endpoints")

router = APIRouter()

@router.post("/sql-query", response_model=SQLQueryResponse)
async def execute_sql_query(
    request: SQLQueryRequest,
    db: Annotated[Session, Depends(get_db)]
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

@router.get("/insights", response_model=BusinessInsightsResponse)
async def get_business_insights(
    user_role: UserRole = UserRole.administrador,
    db: Annotated[Session, Depends(get_db)] = None
) -> BusinessInsightsResponse:
    """
    Obtiene insights automáticos del negocio
    
    - **user_role**: Rol del usuario (determina qué insights son visibles)
    """
    try:
        logger.info(f"Generando insights para rol: {user_role}")
        
        # Solo administradores pueden ver insights completos
        if user_role != UserRole.administrador:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden acceder a los insights completos"
            )
        
        # Obtener servicio de IA
        ai_service = get_ai_service(db)
        
        # Generar insights
        result = await ai_service.get_business_insights(user_role=user_role.value)
        
        return BusinessInsightsResponse(
            success=result["success"],
            insights=result["insights"],
            generated_at=datetime.now(),
            user_role=user_role.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando insights: {str(e)}"
        )

@router.post("/knowledge-query", response_model=KnowledgeQueryResponse)
async def query_knowledge_base(
    request: KnowledgeQueryRequest,
    db: Annotated[Session, Depends(get_db)]
) -> KnowledgeQueryResponse:
    """
    Consulta la base de conocimiento usando RAG (Retrieval-Augmented Generation)
    
    **NOTA**: Esta funcionalidad está en desarrollo y se implementará en la Fase 1.5
    
    - **query**: Pregunta sobre documentación técnica o procedimientos
    - **context**: Contexto adicional para mejorar la respuesta
    - **include_sources**: Si incluir las fuentes de información utilizadas
    """
    try:
        logger.info(f"Consulta de conocimiento: '{request.query}'")
        
        # TODO: Implementar RAG service en la siguiente fase
        return KnowledgeQueryResponse(
            success=False,
            answer=None,
            sources=None,
            confidence=None,
            error="Funcionalidad de RAG en desarrollo. Se implementará en la Fase 1.5"
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

@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(
    feedback: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """
    Submete feedback del usuario sobre respuestas de IA
    """
    logger = get_logger()
    logger.info(f"Recibiendo feedback: usuario_tipo={feedback.user_type}, rating={feedback.rating}")
    
    try:
        # Crear instancia de CRUD
        knowledge_feedback_crud = CRUDKnowledgeFeedback()
        
        # Crear el feedback en la base de datos
        feedback_data = {
            "question": feedback.original_query,
            "expected_answer": feedback.ai_response,
            "user_comment": feedback.user_feedback,
            "rating": feedback.rating,
            "user_type": feedback.user_type,
            "status": "pendiente"
        }
        
        new_feedback = knowledge_feedback_crud.create(db=db, obj_in=feedback_data)
        
        return FeedbackResponse(
            success=True,
            feedback_id=new_feedback.id,
            message="Feedback recibido correctamente"
        )
    except Exception as e:
        logger.error(f"Error al procesar feedback: {str(e)}")
        return FeedbackResponse(
            success=False,
            feedback_id=None,
            message=f"Error interno del servidor: {str(e)}"
        )

@router.get("/health", response_model=AIHealthResponse)
async def check_ai_health(
    db: Annotated[Session, Depends(get_db)]
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
            db.execute("SELECT 1")
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
    db: Annotated[Session, Depends(get_db)] = None
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
        schema_info = ai_service._get_database_schema_info()
        
        return {
            "message": "Información del schema de la base de datos",
            "schema_info": schema_info,
            "available_tables_by_role": ai_service.role_permissions
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo schema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo información del schema: {str(e)}"
        ) 