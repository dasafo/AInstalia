#backend/schemas/ai_schema.py
"""
Esquemas Pydantic para servicios de IA
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

class UserRole(str, Enum):
    """Roles de usuario permitidos"""
    cliente = "cliente"
    tecnico = "tecnico"
    administrador = "administrador"

class SQLQueryRequest(BaseModel):
    """Schema para solicitudes de consulta SQL en lenguaje natural"""
    query: str = Field(..., description="Consulta en lenguaje natural", min_length=5, max_length=500)
    user_role: UserRole = Field(default=UserRole.cliente, description="Rol del usuario")
    user_id: Optional[int] = Field(default=None, description="ID del usuario para filtros específicos")
    include_sql: bool = Field(default=False, description="Si incluir la consulta SQL generada en la respuesta")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "¿Cuántas órdenes he realizado este mes?",
                "user_role": "cliente",
                "user_id": 123,
                "include_sql": False
            }
        }
    )

class SQLQueryResponse(BaseModel):
    """Schema para respuestas de consultas SQL"""
    success: bool = Field(..., description="Si la consulta fue exitosa")
    result: Optional[List[Dict[str, Any]]] = Field(default=None, description="Resultados de la consulta")
    total_results: Optional[int] = Field(default=None, description="Número total de resultados")
    error: Optional[str] = Field(default=None, description="Mensaje de error si aplica")
    sql_query: Optional[str] = Field(default=None, description="Consulta SQL generada (si se solicita)")
    user_role: Optional[str] = Field(default=None, description="Rol del usuario que hizo la consulta")
    execution_time_ms: Optional[float] = Field(default=None, description="Tiempo de ejecución en milisegundos")

    model_config = ConfigDict(from_attributes=True)

class BusinessInsightsResponse(BaseModel):
    """Schema para insights automáticos del negocio"""
    success: bool = Field(..., description="Si la generación de insights fue exitosa")
    insights: Dict[str, Any] = Field(..., description="Insights del negocio")
    generated_at: datetime = Field(..., description="Fecha y hora de generación")
    user_role: str = Field(..., description="Rol del usuario")
    
    model_config = ConfigDict(from_attributes=True)

class KnowledgeQueryRequest(BaseModel):
    """Schema para consultas de conocimiento (RAG) - Para implementación futura"""
    query: str = Field(..., description="Pregunta sobre documentación o conocimiento", min_length=5, max_length=500)
    context: Optional[str] = Field(default=None, description="Contexto adicional para la consulta")
    include_sources: bool = Field(default=True, description="Si incluir fuentes en la respuesta")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "¿Cómo instalar un aire acondicionado modelo XP-400?",
                "context": "Cliente necesita instalación urgente",
                "include_sources": True
            }
        }
    )

class KnowledgeQueryResponse(BaseModel):
    """Schema para respuestas de consultas de conocimiento"""
    success: bool = Field(..., description="Si la consulta fue exitosa")
    answer: Optional[str] = Field(default=None, description="Respuesta generada")
    sources: Optional[List[str]] = Field(default=None, description="Fuentes de información utilizadas")
    confidence: Optional[float] = Field(default=None, description="Nivel de confianza de la respuesta (0-1)")
    error: Optional[str] = Field(default=None, description="Mensaje de error si aplica")

    model_config = ConfigDict(from_attributes=True)

class FeedbackRequest(BaseModel):
    """Schema para envío de feedback sobre respuestas de IA"""
    original_query: str = Field(..., description="Consulta original")
    ai_response: str = Field(..., description="Respuesta de la IA")
    user_feedback: str = Field(..., description="Feedback del usuario")
    rating: Optional[int] = Field(default=None, description="Calificación de 1-5", ge=1, le=5)
    user_type: UserRole = Field(..., description="Tipo de usuario que proporciona feedback")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "original_query": "¿Cuántos productos tengo en stock?",
                "ai_response": "Tienes 150 productos en stock",
                "user_feedback": "La respuesta fue correcta pero me gustaría más detalle",
                "rating": 4,
                "user_type": "administrador"
            }
        }
    )

class FeedbackResponse(BaseModel):
    """Schema para respuesta de feedback enviado"""
    success: bool = Field(..., description="Si el feedback fue registrado exitosamente")
    feedback_id: Optional[int] = Field(default=None, description="ID del feedback registrado")
    message: str = Field(..., description="Mensaje de confirmación")
    
    model_config = ConfigDict(from_attributes=True)

class AIHealthResponse(BaseModel):
    """Schema para estado de salud de los servicios de IA"""
    sql_agent_status: str = Field(..., description="Estado del agente SQL")
    openai_connection: bool = Field(..., description="Estado de conexión con OpenAI")
    database_connection: bool = Field(..., description="Estado de conexión con la base de datos")
    available_roles: List[str] = Field(..., description="Roles de usuario disponibles")
    last_check: datetime = Field(..., description="Última verificación de estado")
    
    model_config = ConfigDict(from_attributes=True)

# Esquemas para estadísticas y métricas
class QueryStats(BaseModel):
    """Estadísticas de uso de consultas"""
    total_queries: int = Field(..., description="Total de consultas realizadas")
    successful_queries: int = Field(..., description="Consultas exitosas")
    failed_queries: int = Field(..., description="Consultas fallidas")
    avg_execution_time: float = Field(..., description="Tiempo promedio de ejecución en ms")
    most_common_role: str = Field(..., description="Rol más frecuente")
    
    model_config = ConfigDict(from_attributes=True)

class AIUsageStats(BaseModel):
    """Estadísticas de uso general de IA"""
    sql_queries: QueryStats = Field(..., description="Estadísticas de consultas SQL")
    knowledge_queries: Optional[QueryStats] = Field(default=None, description="Estadísticas de consultas de conocimiento")
    feedback_received: int = Field(..., description="Total de feedback recibido")
    avg_user_rating: Optional[float] = Field(default=None, description="Calificación promedio de usuarios")
    
    model_config = ConfigDict(from_attributes=True) 