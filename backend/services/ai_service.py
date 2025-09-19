#backend/services/ai_service.py
"""
Servicio de IA con Agente SQL seguro para AInstalia
"""
import re
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, inspect
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from backend.core.config import settings
from backend.core.logging import get_logger
import anyio
from datetime import datetime

logger = get_logger("ainstalia.ai_service")


def _to_sync_dsn(url: Optional[str]) -> Optional[str]:
    """Convierte DSN async (asyncpg) a versión síncrona."""
    if not url:
        return url
    if "://" not in url:
        return url
    scheme, rest = url.split("://", 1)
    if "+" in scheme:
        scheme = scheme.split("+", 1)[0]
    return f"{scheme}://{rest}"


class AIService:
    """Servicio principal de IA con agente SQL seguro"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.llm = self._initialize_llm()
        self.sql_agent = self._initialize_sql_agent()
        
        # Tablas permitidas por rol
        self.role_permissions = {
            "cliente": [
                "clients", "orders", "order_items", "installed_equipment", 
                "interventions", "contracts", "chat_sessions", "chat_messages"
            ],
            "tecnico": [
                "clients", "products", "technicians", "installed_equipment", 
                "interventions", "stock", "warehouses", "orders", "order_items"
            ],
            "administrador": [
                "clients", "products", "technicians", "installed_equipment", 
                "interventions", "contracts", "stock", "warehouses", 
                "orders", "order_items", "chat_sessions", "chat_messages", 
                "knowledge_feedback"
            ]
        }
        
        # Consultas prohibidas (palabras clave peligrosas)
        self.forbidden_keywords = [
            "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", 
            "TRUNCATE", "GRANT", "REVOKE", "EXEC", "EXECUTE"
        ]
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Inicializa el modelo de lenguaje OpenAI"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no está configurada en las variables de entorno")
        
        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def _initialize_sql_agent(self) -> Any:
        """Inicializa el agente SQL de LangChain"""
        try:
            dsn_async = settings.DATABASE_URL
            dsn_env = os.getenv("DATABASE_URL_SYNC")
            sync_dsn = dsn_env or _to_sync_dsn(dsn_async)

            if not sync_dsn:
                logger.warning("No se encontró DSN síncrono para el agente SQL; se omite inicialización")
                return None

            sql_db = SQLDatabase.from_uri(sync_dsn)

            toolkit = SQLDatabaseToolkit(db=sql_db, llm=self.llm)
            
            # Prompt personalizado para el agente
            sql_prompt = PromptTemplate(
                input_variables=["input", "agent_scratchpad", "table_info", "role"],
                template="""
Eres un asistente de IA especializado en consultas SQL para AInstalia, una empresa de mantenimiento industrial.

CONTEXTO DE LA BASE DE DATOS:
{table_info}

ROL DEL USUARIO: {role}

INSTRUCCIONES IMPORTANTES:
1. SOLO generar consultas SELECT (de solo lectura)
2. NO usar: DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE
3. Filtrar resultados según el rol del usuario
4. Usar LIMIT para evitar resultados masivos
5. Responder en español de forma clara y concisa

CONSULTA DEL USUARIO: {input}

{agent_scratchpad}

Genera SOLO la consulta SQL necesaria, sin explicaciones adicionales.
"""
            )
            
            # Crear agente SQL
            agent = create_sql_agent(
                llm=self.llm,
                toolkit=toolkit,
                verbose=True,
                handle_parsing_errors=True
            )
            
            return agent
            
        except Exception as e:
            logger.error(f"Error inicializando agente SQL (dsn síncrono): {e}")
            return None
    
    def _validate_sql_query(self, query: str) -> Tuple[bool, str]:
        """Valida que la consulta SQL sea segura"""
        query_upper = query.upper()
        
        # Verificar palabras prohibidas
        for keyword in self.forbidden_keywords:
            if keyword in query_upper:
                return False, f"Consulta prohibida: contiene '{keyword}'"
        
        # Verificar que sea una consulta SELECT
        if not query_upper.strip().startswith("SELECT"):
            return False, "Solo se permiten consultas SELECT"
        
        # Verificar que tenga LIMIT (agregar si no tiene)
        if "LIMIT" not in query_upper:
            query += " LIMIT 100"
        
        return True, query
    
    def _filter_tables_by_role(self, user_role: str, query: str) -> Tuple[bool, str]:
        """Filtra las tablas según el rol del usuario"""
        allowed_tables = self.role_permissions.get(user_role.lower(), [])
        
        # Buscar nombres de tablas en la consulta
        table_pattern = r'FROM\s+(\w+)|JOIN\s+(\w+)'
        tables_in_query = re.findall(table_pattern, query.upper())
        
        # Aplanar la lista de tuplas
        tables_found = []
        for match in tables_in_query:
            tables_found.extend([t.lower() for t in match if t])
        
        # Verificar permisos
        for table in tables_found:
            if table not in allowed_tables:
                return False, f"No tienes permisos para acceder a la tabla '{table}'"
        
        return True, "Permisos OK"
    
    async def _get_database_schema_info(self) -> str:
        """Obtiene información del schema de la base de datos (asíncrono)"""
        try:
            def _sync_inspect_ops(sync_session):
                inspector = inspect(sync_session.bind)
                tables = inspector.get_table_names()
                
                schema_info_parts = []
                for table_name in tables:
                    columns = inspector.get_columns(table_name)
                    schema_info_parts.append(f"📋 {table_name.upper()}:\n")
                    for column in columns:
                        col_type = str(column['type'])
                        nullable = "NULL" if column['nullable'] else "NOT NULL"
                        schema_info_parts.append(f"   - {column['name']} ({col_type}) {nullable}\n")
                    schema_info_parts.append("\n")
                return "".join(schema_info_parts)

            schema_base_info = await self.db_session.run_sync(_sync_inspect_ops)

            schema_info = "TABLAS DISPONIBLES EN AINSTALIA:\n\n" + schema_base_info
            
            # Agregar información específica del dominio
            schema_info += """
RELACIONES PRINCIPALES:
- clients.client_id → orders.client_id, installed_equipment.client_id, contracts.client_id
- products.sku → order_items.sku, stock.sku, installed_equipment.sku
- technicians.technician_id → interventions.technician_id
- warehouses.warehouse_id → stock.warehouse_id
- orders.order_id → order_items.order_id

EJEMPLOS DE CONSULTAS ÚTILES:
- "¿Cuántos clientes tenemos?" → SELECT COUNT(*) FROM clients;
- "¿Qué productos están en stock bajo?" → SELECT * FROM stock WHERE quantity < min_stock;
- "¿Cuáles son las últimas 5 intervenciones?" → SELECT * FROM interventions ORDER BY date DESC LIMIT 5;
"""
            
            return schema_info
            
        except Exception as e:
            logger.error(f"Error obteniendo schema: {e}")
            return "Error al obtener información del schema"
    
    async def execute_sql_query(
        self, 
        natural_query: str, 
        user_role: str = "cliente",
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta una consulta en lenguaje natural usando el agente SQL
        
        Args:
            natural_query: Consulta en lenguaje natural
            user_role: Rol del usuario (cliente, tecnico, administrador)
            user_id: ID del usuario para filtros adicionales
            
        Returns:
            Dict con resultado, SQL generado y metadatos
        """
        try:
            logger.info(f"Procesando consulta SQL: '{natural_query}' para rol: {user_role}")
            
            # Verificar que el agente esté inicializado
            if not self.sql_agent:
                return {
                    "success": False,
                    "error": "Agente SQL no inicializado",
                    "result": None,
                    "sql_query": None
                }
            
            # Preparar contexto con información del schema
            schema_info = await self._get_database_schema_info()
            
            # Construir prompt con contexto
            full_prompt = f"""
ROL: {user_role.upper()}
USUARIO_ID: {user_id or 'N/A'}

INFORMACIÓN DEL SCHEMA:
{schema_info}

CONSULTA: {natural_query}

INSTRUCCIONES ADICIONALES:
- Si el rol es 'cliente' y se proporciona user_id, filtrar por client_id = {user_id}
- Si el rol es 'tecnico' y se proporciona user_id, mostrar solo información relevante para ese técnico
- Usar LIMIT 20 por defecto para evitar resultados masivos
- Formatear fechas de forma legible
- Responder en español
"""
            
            # Ejecutar consulta con el agente en un hilo separado
            agent_response = await anyio.to_thread.run_sync(self.sql_agent.run, full_prompt)
            
            # Extraer la consulta SQL del response del agente
            sql_query = self._extract_sql_from_response(agent_response)
            
            if not sql_query:
                return {
                    "success": False,
                    "error": "No se pudo extraer la consulta SQL del agente",
                    "result": agent_response, # Devolver la respuesta cruda del agente para depuración
                    "sql_query": None
                }
            
            # Validar y filtrar consulta SQL
            is_valid, message = self._validate_sql_query(sql_query)
            if not is_valid:
                return {
                    "success": False,
                    "error": message,
                    "result": None,
                    "sql_query": sql_query
                }
            
            is_allowed, message = self._filter_tables_by_role(user_role, sql_query)
            if not is_allowed:
                return {
                    "success": False,
                    "error": message,
                    "result": None,
                    "sql_query": sql_query
                }
            
            # Ejecutar consulta SQL validada asíncronamente
            logger.info(f"Ejecutando SQL validado: {sql_query}")
            
            # Aquí es donde realmente ejecutas la consulta en la DB de forma asíncrona
            # Usar db_session directamente con execute para consultas SELECT
            # Asegúrate de que el resultado sea un ScalarResult antes de llamar a all()
            result_proxy = await self.db_session.execute(text(sql_query))
            
            # Para resultados de SELECT, generalmente necesitas obtener los resultados
            # de una manera que preserve el formato de columna
            # Esto puede variar dependiendo de lo que el agente devuelva, podría ser necesario un ajuste
            rows = result_proxy.fetchall()
            
            # Formatear el resultado como lista de diccionarios
            # Obtener nombres de columnas
            column_names = list(result_proxy.keys())
            formatted_results = [
                dict(zip(column_names, row))
                for row in rows
            ]
            
            return {
                "success": True,
                "error": None,
                "result": formatted_results,
                "sql_query": sql_query
            }
            
        except Exception as e:
            logger.error(f"Error en execute_sql_query: {e}")
            return {
                "success": False,
                "error": f"Error interno del servicio de IA: {str(e)}",
                "result": None,
                "sql_query": None
            }
            
    def _extract_sql_from_response(self, agent_response: str) -> Optional[str]:
        """
        Extrae la consulta SQL de la respuesta del agente LangChain.
        Se asume que la consulta SQL está en un bloque de código markdown.
        """
        match = re.search(r"```sql\n(.*?)\n```", agent_response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    async def _table_columns(self, table: str, schema: str = "public") -> set[str]:
        """Obtiene el conjunto de columnas disponibles para una tabla."""
        query = text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = :table"
        )
        try:
            result = await self.db_session.execute(query, {"schema": schema, "table": table})
            columns = {row[0] for row in result.fetchall()}
            return columns
        except Exception as exc:
            logger.error(f"Error inspeccionando columnas de {schema}.{table}: {exc}")
            return set()

    async def get_business_insights(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Genera insights de negocio con contrato estable."""
        payload = payload or {}
        params = payload.get("params") or {}
        raw_role = params.get("user_role") or payload.get("user_role") or "administrador"
        user_role = raw_role.lower() if isinstance(raw_role, str) else "administrador"

        if user_role != "administrador":
            return {
                "success": False,
                "error": "Solo los administradores pueden acceder a los insights completos."
            }

        try:
            query = (payload.get("query") or "").strip().lower()
            insights: List[Dict[str, Any]] = []
            warnings: List[str] = []

            async def _fetch_scalar(sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
                result = await self.db_session.execute(text(sql), params or {})
                for attr in ("scalar_one_or_none", "scalar_one", "scalar"):
                    getter = getattr(result, attr, None)
                    if callable(getter):
                        try:
                            return getter()
                        except Exception:
                            continue
                return None

            try:
                total_contracts = int(await _fetch_scalar("SELECT COUNT(*) FROM contracts;") or 0)
                insights.append({"metric": "total_contracts", "value": total_contracts})
            except Exception as exc:
                logger.error(f"Error obteniendo total_contracts: {exc}")
                return {"success": False, "error": "No se pudo calcular métricas de contratos."}

            contract_cols = await self._table_columns("contracts")

            active_value: Optional[int] = None
            if {"status"}.issubset(contract_cols):
                active_value = await _fetch_scalar(
                    "SELECT COUNT(*) FROM contracts WHERE status IN (:active, :activo, :enabled)",
                    {"active": "active", "activo": "activo", "enabled": "enabled"}
                )
            elif "active" in contract_cols:
                active_value = await _fetch_scalar(
                    "SELECT COUNT(*) FROM contracts WHERE active IS TRUE"
                )
            elif "is_active" in contract_cols:
                active_value = await _fetch_scalar(
                    "SELECT COUNT(*) FROM contracts WHERE is_active IS TRUE"
                )
            else:
                warnings.append("contracts.status no existe; métrica active_contracts omitida")

            if active_value is not None:
                try:
                    insights.append({"metric": "active_contracts", "value": int(active_value or 0)})
                except Exception:
                    warnings.append("No se pudo convertir active_contracts a entero")

            if "created_at" in contract_cols:
                recent_value = await _fetch_scalar(
                    "SELECT COUNT(*) FROM contracts WHERE created_at >= NOW() - INTERVAL '30 days'"
                )
            elif "createdon" in contract_cols:
                recent_value = await _fetch_scalar(
                    "SELECT COUNT(*) FROM contracts WHERE createdon >= NOW() - INTERVAL '30 days'"
                )
            else:
                recent_value = None
                warnings.append("contracts.created_at no existe; métrica recientes_30d omitida")

            if recent_value is not None:
                try:
                    insights.append({"metric": "recent_contracts_30d", "value": int(recent_value or 0)})
                except Exception:
                    warnings.append("No se pudo convertir recent_contracts_30d a entero")

            if query and query not in ("overview", "resumen"):
                insights.append({
                    "metric": "note",
                    "value": f"No existe una vista específica para '{query}'. Se devuelve el resumen general."
                })

            for warning in warnings:
                insights.append({"note": warning})

            return {"success": True, "insights": insights}
        except Exception as exc:
            logger.error(f"Error generando insights de negocio: {exc}")
            return {"success": False, "error": f"Error generando insights: {str(exc)}"}

    async def get_health_status(self) -> Dict[str, Any]:
        """Obtiene el estado de salud de los componentes de IA"""
        status_info = {
            "llm_connection": False,
            "sql_agent_initialized": False,
            "db_connection": False,
            "rag_service_initialized": False, # Asumiendo que el RAGService será inyectado si es necesario
            "status": "unhealthy",
            "message": "Servicios de IA no completamente funcionales"
        }

        # Verificar conexión con LLM (OpenAI)
        try:
            self.llm.invoke("Hello")
            status_info["llm_connection"] = True
        except Exception as e:
            logger.error(f"Fallo de conexión con LLM: {e}")

        # Verificar inicialización del agente SQL
        if self.sql_agent is not None:
            status_info["sql_agent_initialized"] = True

        # Verificar conexión con la base de datos (usando la sesión asíncrona)
        try:
            await self.db_session.execute(text("SELECT 1"))
            status_info["db_connection"] = True
        except Exception as e:
            logger.error(f"Fallo de conexión con DB: {e}")

        if status_info["llm_connection"] and status_info["sql_agent_initialized"] and status_info["db_connection"]:
            status_info["status"] = "healthy"
            status_info["message"] = "Todos los servicios de IA están operativos"
        
        return status_info

    def get_usage_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de uso de la IA (simulado por ahora)"""
        # Esto es un placeholder. En una aplicación real, obtendría esto de logs o una DB de métricas
        return {
            "sql_queries_executed": 125,
            "knowledge_queries_executed": 78,
            "feedback_submitted": 34,
            "ai_errors": 5,
            "last_reset": datetime.now().isoformat()
        }

def get_ai_service(db_session: AsyncSession) -> AIService:
    """Factory function para crear instancia del servicio AI"""
    return AIService(db_session) 
