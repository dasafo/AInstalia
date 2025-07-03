#backend/services/ai_service.py
"""
Servicio de IA con Agente SQL seguro para AInstalia
"""
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from backend.core.config import settings
from backend.core.logging import get_logger
import anyio

logger = get_logger("ainstalia.ai_service")

class AIService:
    """Servicio principal de IA con agente SQL seguro"""
    
    def __init__(self, db_session: Session):
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
            # Crear conexión SQL para LangChain
            db_url = settings.DATABASE_URL
            sql_db = SQLDatabase.from_uri(db_url)
            
            # Crear toolkit SQL
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
            logger.error(f"Error inicializando agente SQL: {e}")
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
    
    def _get_database_schema_info(self) -> str:
        """Obtiene información del schema de la base de datos"""
        try:
            inspector = inspect(self.db_session.bind)
            tables = inspector.get_table_names()
            
            schema_info = "TABLAS DISPONIBLES EN AINSTALIA:\n\n"
            
            for table_name in tables:
                columns = inspector.get_columns(table_name)
                schema_info += f"📋 {table_name.upper()}:\n"
                
                for column in columns:
                    col_type = str(column['type'])
                    nullable = "NULL" if column['nullable'] else "NOT NULL"
                    schema_info += f"   - {column['name']} ({col_type}) {nullable}\n"
                
                schema_info += "\n"
            
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
            schema_info = self._get_database_schema_info()
            
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
            
            # Ejecutar consulta con el agente
            agent_response = self.sql_agent.run(full_prompt)
            
            # Extraer la consulta SQL del response del agente
            sql_query = self._extract_sql_from_response(agent_response)
            
            if not sql_query:
                return {
                    "success": False,
                    "error": "No se pudo generar consulta SQL válida",
                    "result": agent_response,
                    "sql_query": None
                }
            
            # Validar consulta SQL
            is_valid, final_query = self._validate_sql_query(sql_query)
            if not is_valid:
                return {
                    "success": False,
                    "error": final_query,  # final_query contains the error message
                    "result": None,
                    "sql_query": sql_query
                }
            
            # Verificar permisos por rol
            has_permission, permission_message = self._filter_tables_by_role(user_role, final_query)
            if not has_permission:
                return {
                    "success": False,
                    "error": permission_message,
                    "result": None,
                    "sql_query": final_query
                }
            
            # Ejecutar consulta SQL validada
            result = await anyio.to_thread.run_sync(self.db_session.execute, text(final_query))
            result = await anyio.to_thread.run_sync(result.fetchall)
            
            # Convertir resultado a formato serializable
            formatted_result = []
            for row in result:
                formatted_result.append(dict(row._mapping))
            
            logger.info(f"Consulta ejecutada exitosamente. Resultados: {len(formatted_result)}")
            
            return {
                "success": True,
                "error": None,
                "result": formatted_result,
                "sql_query": final_query,
                "total_results": len(formatted_result),
                "user_role": user_role
            }
            
        except Exception as e:
            logger.error(f"Error ejecutando consulta SQL: {e}")
            return {
                "success": False,
                "error": f"Error interno: {str(e)}",
                "result": None,
                "sql_query": None
            }
    
    def _extract_sql_from_response(self, agent_response: str) -> Optional[str]:
        """Extrae la consulta SQL de la respuesta del agente"""
        try:
            # Buscar patrones SQL en la respuesta
            sql_patterns = [
                r'```sql\n(.*?)\n```',  # Código SQL en bloques
                r'```\n(SELECT.*?)\n```',  # SELECT en bloques
                r'(SELECT.*?);',  # SELECT con punto y coma
                r'(SELECT.*?)(?:\n|$)'  # SELECT hasta final de línea
            ]
            
            for pattern in sql_patterns:
                match = re.search(pattern, agent_response, re.IGNORECASE | re.DOTALL)
                if match:
                    sql_query = match.group(1).strip()
                    if sql_query.upper().startswith('SELECT'):
                        return sql_query
            
            # Si no encuentra patrones, devolver la respuesta completa si parece SQL
            if agent_response.upper().strip().startswith('SELECT'):
                return agent_response.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo SQL: {e}")
            return None
    
    async def get_business_insights(self, user_role: str = "administrador") -> Dict[str, Any]:
        """Genera insights automáticos del negocio"""
        insights_queries = {
            "total_clientes": "SELECT COUNT(*) as total FROM clients",
            "total_productos": "SELECT COUNT(*) as total FROM products", 
            "ordenes_pendientes": "SELECT COUNT(*) as total FROM orders WHERE status = 'pendiente'",
            "stock_bajo": "SELECT COUNT(*) as total FROM stock WHERE quantity < min_stock",
            "intervenciones_mes": """
                SELECT COUNT(*) as total 
                FROM interventions 
                WHERE date >= DATE_TRUNC('month', CURRENT_DATE)
            """,
            "top_productos": """
                SELECT p.name, SUM(oi.quantity) as total_vendido
                FROM products p
                JOIN order_items oi ON p.sku = oi.sku
                GROUP BY p.name
                ORDER BY total_vendido DESC
                LIMIT 5
            """
        }
        
        insights = {}
        
        for key, query in insights_queries.items():
            try:
                result = await anyio.to_thread.run_sync(self.db_session.execute, text(query))
                insights[key] = await anyio.to_thread.run_sync(result.fetchall)
                insights[key] = [dict(row._mapping) for row in insights[key]]
            except Exception as e:
                logger.error(f"Error en insight {key}: {e}")
                insights[key] = f"Error: {str(e)}"
        
        return {
            "success": True,
            "insights": insights,
            "generated_at": "now",
            "user_role": user_role
        }

# Función de utilidad para crear instancia del servicio
def get_ai_service(db_session: Session) -> AIService:
    """Factory function para crear instancia del servicio de IA"""
    return AIService(db_session) 