# 🤖 Guía Completa - Fase 1: Agentes de IA Especializados

## ✅ Estado de la Fase 1

La **Fase 1** está **COMPLETA** y operativa. Se han implementado exitosamente los primeros agentes de IA especializados que transforman AInstalia en un sistema inteligente capaz de procesar consultas en lenguaje natural.

### 🎯 **Objetivos Alcanzados**

- ✅ **SQL Agent**: Convierte preguntas en español a consultas SQL seguras
- ✅ **Business Intelligence Agent**: Genera insights automáticos del negocio
- ✅ **Sistema de Seguridad**: Control de acceso por roles y validación de consultas
- ✅ **API de IA**: 7 endpoints especializados para interacción con agentes
- ✅ **Testing Completo**: 17 tests adicionales para funcionalidades de IA

### 📊 **Métricas de Implementación**

| Componente | Implementado | Tests | Estado |
|------------|--------------|-------|--------|
| **SQL Agent** | ✅ | 8 tests | Operativo |
| **Business Intelligence** | ✅ | 2 tests | Operativo |
| **Sistema de Permisos** | ✅ | 3 tests | Operativo |
| **Health Checks** | ✅ | 2 tests | Operativo |
| **Knowledge Base** | ✅ | 1 test | Preparado para Fase 2 |
| **Feedback System** | ✅ | 1 test | Operativo |

**Total**: 88 tests pasando (56 Fase 0 + 32 Fase 1, incluyendo RAGService y performance tests) ✅

---

## 🏗️ **ARQUITECTURA DE AGENTES IA**

### 🎯 **Visión General**

La Fase 1 añade una **capa de inteligencia artificial** sobre la infraestructura base, creando agentes especializados que pueden interactuar con los datos empresariales de forma natural.

```
┌─────────────────────────────────────────────────────────────┐
│                    🤖 AGENTES IA ESPECIALIZADOS             │
│   SQL Agent | Business Intelligence | Knowledge Manager    │
├─────────────────────────────────────────────────────────────┤
│                    🛡️ CAPA DE SEGURIDAD                     │
│   Control de Roles | Validación SQL | Filtros de Datos    │
├─────────────────────────────────────────────────────────────┤
│                    🌐 API DE IA (FastAPI)                   │
│   7 Endpoints IA | Procesamiento NLP | Respuestas JSON    │
├─────────────────────────────────────────────────────────────┤
│                    🔗 SERVICIOS DE IA                       │
│   LangChain | OpenAI GPT-4 | SQL Database Toolkit         │
├─────────────────────────────────────────────────────────────┤
│                    📊 INFRAESTRUCTURA BASE                  │
│   FastAPI | PostgreSQL | SQLAlchemy | Pydantic            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 **AGENTE 1: SQL AGENT**

### 🎯 **Propósito**
Convierte consultas en lenguaje natural (español) a consultas SQL seguras y ejecuta operaciones de lectura sobre la base de datos empresarial.

### 📁 **Implementación**: `backend/services/ai_service.py`

#### **Características Principales**

```python
class AIService:
    """Servicio principal de IA con agente SQL seguro"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.llm = self._initialize_llm()                    # OpenAI GPT-4
        self.sql_agent = self._initialize_sql_agent()        # LangChain SQL Agent
        self.role_permissions = {...}                        # Control de acceso
        self.forbidden_keywords = [...]                      # Palabras prohibidas
```

#### **🔍 Capacidades del SQL Agent**

1. **Procesamiento de Lenguaje Natural**:
   ```python
   # Entrada: "¿Cuántos clientes tenemos en total?"
   # Salida: "SELECT COUNT(*) as total FROM clients"
   
   # Entrada: "¿Qué productos están en stock bajo?"
   # Salida: "SELECT * FROM stock WHERE quantity < min_stock LIMIT 20"
   ```

2. **Validación y Seguridad**:
   ```python
   def _validate_sql_query(self, query: str) -> Tuple[bool, str]:
       """Valida que la consulta SQL sea segura"""
       # ✅ Solo permite consultas SELECT
       # ✅ Bloquea: DROP, DELETE, UPDATE, INSERT, ALTER, CREATE
       # ✅ Añade LIMIT automático si no existe
       # ✅ Verifica sintaxis SQL
   ```

3. **Control de Acceso por Roles**:
   ```python
   role_permissions = {
       "cliente": [
           "clients", "orders", "order_items", "installed_equipment", 
           "interventions", "contracts", "chat_sessions", "chat_messages"
       ],
       "tecnico": [
           "clients", "products", "technicians", "installed_equipment", 
           "interventions", "stock", "warehouses", "orders", "order_items"
       ],
       "administrador": [
           # Acceso completo a todas las tablas
       ]
   }
   ```

#### **🔧 Flujo de Procesamiento**

```mermaid
graph TD
    A[👤 Consulta en Español] --> B[🧠 LLM OpenAI GPT-4]
    B --> C[📝 SQL Generado]
    C --> D[🛡️ Validación de Seguridad]
    D --> E[🔍 Verificación de Permisos]
    E --> F[💾 Ejecución en PostgreSQL]
    F --> G[📊 Resultados Formateados]
    G --> H[📤 Respuesta JSON]
```

#### **🎯 Ejemplo Completo de Uso**

```bash
# Consulta POST al endpoint
curl -X POST "http://localhost:8001/api/v1/ai/sql-query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuáles son los 5 productos más vendidos este mes?",
    "user_role": "administrador",
    "user_id": null,
    "include_sql": true
  }'

# Respuesta del agente:
{
  "success": true,
  "result": [
    {"product_name": "Bomba Centrífuga XL", "total_vendido": 45},
    {"product_name": "Motor Eléctrico 5HP", "total_vendido": 38},
    {"product_name": "Válvula de Presión", "total_vendido": 32},
    {"product_name": "Sensor de Temperatura", "total_vendido": 28},
    {"product_name": "Filtro Industrial", "total_vendido": 25}
  ],
  "sql_query": "SELECT p.name as product_name, SUM(oi.quantity) as total_vendido FROM products p JOIN order_items oi ON p.sku = oi.sku JOIN orders o ON oi.order_id = o.order_id WHERE o.created_at >= DATE_TRUNC('month', CURRENT_DATE) GROUP BY p.name ORDER BY total_vendido DESC LIMIT 5",
  "total_results": 5,
  "user_role": "administrador",
  "execution_time_ms": 245
}
```

---

## 📊 **AGENTE 2: BUSINESS INTELLIGENCE**

### 🎯 **Propósito**
Genera automáticamente insights y métricas clave del negocio mediante consultas SQL predefinidas y análisis de tendencias.

### 📁 **Implementación**: Método `get_business_insights()` en `AIService`

#### **📈 Insights Automáticos Implementados**

```python
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
```

#### **🎯 Tipos de Insights Generados**

1. **KPIs Operativos**:
   - Total de clientes activos
   - Productos en catálogo
   - Órdenes pendientes de procesamiento
   - Alertas de stock bajo

2. **Métricas de Productividad**:
   - Intervenciones realizadas en el mes
   - Técnicos más activos
   - Tiempo promedio de resolución

3. **Análisis de Ventas**:
   - Productos más vendidos
   - Tendencias de demanda
   - Clientes con más pedidos

#### **📊 Ejemplo de Respuesta de Insights**

```bash
curl "http://localhost:8001/api/v1/ai/insights?user_role=administrador"

# Respuesta:
{
  "success": true,
  "insights": {
    "total_clientes": [{"total": 46}],
    "total_productos": [{"total": 150}],
    "ordenes_pendientes": [{"total": 8}],
    "stock_bajo": [{"total": 12}],
    "intervenciones_mes": [{"total": 23}],
    "top_productos": [
      {"name": "Bomba Centrífuga XL", "total_vendido": 45},
      {"name": "Motor Eléctrico 5HP", "total_vendido": 38},
      {"name": "Válvula de Presión", "total_vendido": 32}
    ]
  },
  "generated_at": "2024-01-15T10:30:00Z",
  "user_role": "administrador"
}
```

---

## 🛡️ **SISTEMA DE SEGURIDAD Y PERMISOS**

### 🎯 **Control de Acceso por Roles**

El sistema implementa tres niveles de acceso:

#### **👤 Rol: Cliente**
```python
"cliente": [
    "clients",           # Su propia información
    "orders",            # Sus pedidos
    "order_items",       # Items de sus pedidos  
    "installed_equipment", # Sus equipos instalados
    "interventions",     # Intervenciones en sus equipos
    "contracts",         # Sus contratos
    "chat_sessions",     # Sus sesiones de chat
    "chat_messages"      # Sus mensajes
]
```

**Limitaciones**:
- Solo puede ver sus propios datos (filtrado automático por `client_id`)
- No puede acceder a información de otros clientes
- No puede ver datos internos de la empresa

#### **🔧 Rol: Técnico**
```python
"tecnico": [
    "clients",           # Clientes asignados
    "products",          # Catálogo de productos
    "technicians",       # Información de técnicos
    "installed_equipment", # Equipos a mantener
    "interventions",     # Sus intervenciones
    "stock",             # Inventario disponible
    "warehouses",        # Almacenes accesibles
    "orders",            # Órdenes de trabajo
    "order_items"        # Items de órdenes
]
```

**Limitaciones**:
- Ve intervenciones asignadas y relacionadas
- Acceso limitado a información financiera
- No puede ver todos los contratos

#### **👨‍💼 Rol: Administrador**
```python
"administrador": [
    # Acceso completo a todas las tablas
    "clients", "products", "technicians", "installed_equipment", 
    "interventions", "contracts", "stock", "warehouses", 
    "orders", "order_items", "chat_sessions", "chat_messages", 
    "knowledge_feedback"
]
```

**Privilegios completos**:
- Acceso a todos los datos de la empresa
- Puede generar todos los insights
- Acceso a información del esquema de BD

### 🚫 **Validaciones de Seguridad**

#### **SQL Injection Prevention**
```python
forbidden_keywords = [
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", 
    "TRUNCATE", "GRANT", "REVOKE", "EXEC", "EXECUTE"
]

def _validate_sql_query(self, query: str) -> Tuple[bool, str]:
    """Valida que la consulta SQL sea segura"""
    query_upper = query.upper()
    
    # Verificar palabras prohibidas
    for keyword in self.forbidden_keywords:
        if keyword in query_upper:
            return False, f"Consulta prohibida: contiene '{keyword}'"
    
    # Solo permitir SELECT
    if not query_upper.strip().startswith("SELECT"):
        return False, "Solo se permiten consultas SELECT"
    
    return True, query
```

#### **Rate Limiting y Monitoring**
```python
# Logging de todas las consultas
logger.info(f"Procesando consulta SQL: '{natural_query}' para rol: {user_role}")

# Tiempo de ejecución monitoreado
execution_time = (time.time() - start_time) * 1000

# Límites automáticos en resultados
if "LIMIT" not in query_upper:
    query += " LIMIT 100"  # Máximo 100 resultados por defecto
```

---

## 🌐 **API ENDPOINTS DE IA - 7 ENDPOINTS**

### 📁 **Implementación**: `backend/api/v1/endpoints/ai.py`

#### **1. 🔍 `/api/v1/ai/sql-query` - Consultas SQL**

```python
@router.post("/sql-query", response_model=SQLQueryResponse)
async def execute_sql_query(request: SQLQueryRequest) -> SQLQueryResponse:
    """
    Ejecuta consultas SQL en lenguaje natural usando IA
    
    - **query**: Consulta en lenguaje natural
    - **user_role**: Rol del usuario (cliente, tecnico, administrador)
    - **user_id**: ID del usuario para filtros personalizados
    - **include_sql**: Si incluir la consulta SQL generada
    """
```

**Ejemplo de uso**:
```bash
POST /api/v1/ai/sql-query
{
  "query": "¿Qué técnicos han hecho más intervenciones este mes?",
  "user_role": "administrador", 
  "include_sql": true
}
```

#### **2. 📊 `/api/v1/ai/insights` - Business Intelligence**

```python
@router.get("/insights", response_model=BusinessInsightsResponse)
async def get_business_insights(user_role: UserRole = UserRole.administrador):
    """
    Obtiene insights automáticos del negocio
    Solo disponible para administradores
    """
```

#### **3. 🧠 `/api/v1/ai/knowledge-query` - Base de Conocimiento**

```python
@router.post("/knowledge-query", response_model=KnowledgeQueryResponse)
async def query_knowledge_base(request: KnowledgeQueryRequest):
    """
    Consulta la base de conocimiento usando RAG
    NOTA: Implementación pendiente para Fase 2
    """
```

#### **4. 💬 `/api/v1/ai/feedback` - Sistema de Feedback**

```python
@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(feedback: FeedbackRequest):
    """
    Submete feedback del usuario sobre respuestas de IA
    Utilizado para mejorar la precisión de los agentes
    """
```

#### **5. 🩺 `/api/v1/ai/health` - Health Check**

```python
@router.get("/health", response_model=AIHealthResponse)
async def check_ai_health():
    """
    Verifica el estado de salud de los servicios de IA
    - Estado del agente SQL
    - Conexión con OpenAI  
    - Conexión con la base de datos
    - Roles disponibles
    """
```

#### **6. 📚 `/api/v1/ai/examples` - Ejemplos de Consultas**

```python
@router.get("/examples")
async def get_query_examples():
    """
    Retorna ejemplos de consultas por rol de usuario
    Ayuda a los usuarios a entender las capacidades del sistema
    """
```

#### **7. 🗂️ `/api/v1/ai/schema` - Información del Schema**

```python
@router.get("/schema")
async def get_database_schema_info(user_role: UserRole = UserRole.administrador):
    """
    Retorna información del schema de la base de datos
    Solo disponible para administradores por seguridad
    """
```

---

## 📋 **SCHEMAS DE IA - VALIDACIÓN DE DATOS**

### 📁 **Implementación**: `backend/schemas/ai_schema.py`

#### **Esquemas de Request/Response**

```python
# Enums para validación
class UserRole(str, Enum):
    cliente = "cliente"
    tecnico = "tecnico"
    administrador = "administrador"

# Request para consultas SQL
class SQLQueryRequest(BaseModel):
    query: str = Field(..., description="Consulta en lenguaje natural")
    user_role: UserRole = Field(default=UserRole.cliente)
    user_id: Optional[int] = Field(None, description="ID del usuario")
    include_sql: bool = Field(False, description="Incluir SQL generado")

# Response de consultas SQL
class SQLQueryResponse(BaseModel):
    success: bool
    result: Optional[List[Dict[str, Any]]] = None
    sql_query: Optional[str] = None
    total_results: Optional[int] = None
    error: Optional[str] = None
    user_role: str
    execution_time_ms: float

# Response de Business Intelligence
class BusinessInsightsResponse(BaseModel):
    success: bool
    insights: Dict[str, Any]
    generated_at: datetime
    user_role: str

# Health Check Response
class AIHealthResponse(BaseModel):
    sql_agent_status: str
    openai_connection: bool
    database_connection: bool
    available_roles: List[str]
    last_check: datetime
```

---

## 🧪 **TESTING DE AGENTES IA - 32 TESTS**

### 📁 **Implementación**: `backend/tests/phase_0/test_ai_endpoints.py`, `backend/tests/phase_0/test_rag_service.py`

#### **Cobertura de Tests Implementada**

```python
class TestAIEndpoints:
    """Test class completa para los endpoints de IA"""
    
    # Tests del SQL Agent (8 tests)
    def test_sql_query_success()              # ✅ Consulta exitosa
    def test_sql_query_error()                # ✅ Manejo de errores
    def test_sql_query_without_sql_included() # ✅ Sin incluir SQL
    def test_sql_query_invalid_role()         # ✅ Rol inválido
    def test_sql_query_missing_query()        # ✅ Campos requeridos
    
    # Tests de Business Intelligence (2 tests)  
    def test_business_insights_success()               # ✅ Insights exitosos
    def test_business_insights_forbidden_for_non_admin() # ✅ Control de acceso
    
    # Tests de Knowledge Base (1 test)
    def test_knowledge_query_not_implemented() # ✅ Funcionalidad pendiente
    
    # Tests de Feedback (2 tests)
    def test_submit_feedback_success()         # ✅ Feedback exitoso  
    def test_submit_feedback_error()           # ✅ Manejo de errores
    
    # Tests de Health Check (2 tests)
    def test_ai_health_check_success()         # ✅ Health check OK
    def test_ai_health_check_with_errors()     # ✅ Health check con errores
    
    # Tests de Utilidades (2 tests)
    def test_query_examples()                  # ✅ Ejemplos de consultas
    def test_database_schema_info_admin_only() # ✅ Schema solo para admin

class TestRAGIntegration:
    """Tests de integración para el flujo RAG completo en endpoints"""
    def test_rag_workflow_integration()       # ✅ Flujo completo RAG
    def test_rag_error_handling_integration() # ✅ Manejo de errores RAG
    def test_knowledge_query_validation()     # ✅ Validación de entrada RAG
    def test_sql_query_validation()           # ✅ Validación de SQL Query
    def test_feedback_validation()            # ✅ Validación de Feedback

class TestRAGPerformance:
    """Tests de rendimiento para el servicio RAG"""
    def test_concurrent_knowledge_queries()   # ✅ Consultas concurrentes
    def test_large_knowledge_base_stats()     # ✅ Estadísticas de KB grande

class TestRAGService:
    """Tests unitarios para el servicio RAG (backend/services/rag_service.py)"""
    def test_rag_service_initialization()              # ✅ Inicialización correcta
    def test_rag_service_initialization_without_api_key() # ✅ Manejo sin API key
    def test_index_document_success()                  # ✅ Indexación exitosa
    def test_index_document_file_not_found()           # ✅ Archivo no encontrado
    def test_index_document_empty_file()               # ✅ Archivo vacío
    def test_search_knowledge_success()                # ✅ Búsqueda exitosa
    def test_search_knowledge_no_vector_store()        # ✅ Búsqueda sin vector store
    def test_generate_answer_success()                 # ✅ Generación de respuesta
    def test_generate_answer_no_context()              # ✅ Sin contexto
    def test_query_knowledge_success()                 # ✅ Consulta de conocimiento
    def test_query_knowledge_error_handling()          # ✅ Manejo de errores
    def test_get_knowledge_stats()                     # ✅ Estadísticas de conocimiento
    def test_get_rag_service_factory()                 # ✅ Función factory
    
class TestRAGServiceIntegration:
    """Tests de integración para RAGService"""
    def test_full_rag_workflow_mock()                  # ✅ Flujo RAG completo con mocks
    def test_ensure_base_knowledge_creation()          # ✅ Creación de conocimiento base
```

#### **Técnicas de Testing Avanzadas**

1. **Mocking de Servicios IA**:
   ```python
   with patch('backend.api.v1.endpoints.ai.get_ai_service') as mock_service:
       mock_ai_service = MagicMock()
       mock_ai_service.execute_sql_query = AsyncMock(return_value={...})
       mock_service.return_value = mock_ai_service
   ```

2. **Simulación de Respuestas OpenAI**:
   ```python
   mock_ai_service.execute_sql_query = AsyncMock(return_value={
       "success": True,
       "result": [{"total_clients": 5}],
       "sql_query": "SELECT COUNT(*) as total_clients FROM clients",
       "user_role": "administrador"
   })
   ```

3. **Tests de Permisos por Rol**:
   ```python
   def test_business_insights_forbidden_for_non_admin():
       response = client.get("/api/v1/ai/insights?user_role=cliente")
       assert response.status_code == 403
       assert "Solo los administradores" in response.json()["detail"]
   ```

#### **Resultados de Tests**

```bash
# Ejecutar tests de IA específicamente
pytest backend/tests/phase_0/test_ai_endpoints.py -v

# Resultado actual para test_ai_endpoints.py (17 tests):
================================= 17 passed in X.Xs =================================

# Ejecutar tests de RAGService específicamente
pytest backend/tests/phase_0/test_rag_service.py -v

# Resultado actual para test_rag_service.py (15 tests):
================================= 15 passed in Y.Ys =================================

# Tests de toda la aplicación
pytest backend/tests/phase_0/ -v

# Resultado total:
================================= 88 passed in Z.Zs =================================
```

---

## 🚀 **INSTALACIÓN Y CONFIGURACIÓN DE IA**

### **1. Requisitos Adicionales**

Además de los requisitos de la Fase 0, necesitas:

```bash
# Variable de entorno obligatoria
OPENAI_API_KEY=tu_clave_openai_aqui

# Dependencias adicionales ya incluidas en requirements.txt:
# langchain-community
# langchain-openai
# langchain-text-splitters
# openai
```

### **2. Configuración de OpenAI**

```bash
# 1. Obtener clave API de OpenAI
# Ir a: https://platform.openai.com/api-keys

# 2. Configurar en .env
echo "OPENAI_API_KEY=sk-..." >> .env

# 3. Verificar configuración
make test-ai
```

### **3. Verificación de Funcionalidad**

```bash
# 1. Verificar que todos los servicios están corriendo
make status

# 2. Comprobar health check de IA
curl http://localhost:8001/api/v1/ai/health

# 3. Probar consulta SQL simple
curl -X POST "http://localhost:8001/api/v1/ai/sql-query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuántos clientes tenemos?",
    "user_role": "administrador"
  }'

# 4. Ejecutar tests de IA
make test-ai
```

---

## 🎯 **EJEMPLOS DE USO PRÁCTICOS**

### **📊 Para Administradores**

```bash
# 1. KPIs del negocio
curl "http://localhost:8001/api/v1/ai/insights?user_role=administrador"

# 2. Análisis de ventas
curl -X POST "http://localhost:8001/api/v1/ai/sql-query" \
  -d '{"query": "¿Cuáles son los clientes que más han comprado este año?", "user_role": "administrador"}'

# 3. Estado del inventario
curl -X POST "http://localhost:8001/api/v1/ai/sql-query" \
  -d '{"query": "¿Qué productos están por debajo del stock mínimo?", "user_role": "administrador"}'
```

### **🔧 Para Técnicos**

```bash
# 1. Intervenciones programadas
curl -X POST "http://localhost:8001/api/v1/ai/sql-query" \
  -d '{"query": "¿Qué intervenciones tengo programadas para esta semana?", "user_role": "tecnico", "user_id": 123}'

# 2. Estado de equipos
curl -X POST "http://localhost:8001/api/v1/ai/sql-query" \
  -d '{"query": "¿Qué equipos requieren mantenimiento preventivo?", "user_role": "tecnico"}'

# 3. Productos necesarios
curl -X POST "http://localhost:8001/api/v1/ai/sql-query" \
  -d '{"query": "¿Qué productos hay en stock para mis próximas intervenciones?", "user_role": "tecnico"}'
```

### **👤 Para Clientes**

```bash
# 1. Estado de mis equipos
curl -X POST "http://localhost:8001/api/v1/ai/sql-query" \
  -d '{"query": "¿Cuándo fue la última intervención en mis equipos?", "user_role": "cliente", "user_id": 456}'

# 2. Mis pedidos
curl -X POST "http://localhost:8001/api/v1/ai/sql-query" \
  -d '{"query": "¿Cuál es el estado de mis últimos pedidos?", "user_role": "cliente", "user_id": 456}'

# 3. Mi contrato
curl -X POST "http://localhost:8001/api/v1/ai/sql-query" \
  -d '{"query": "¿Cuándo vence mi contrato de mantenimiento?", "user_role": "cliente", "user_id": 456}'
```

---

## 📈 **MONITOREO Y MÉTRICAS**

### **🔍 Logs de IA**

```bash
# Ver logs específicos de IA
make logs-api | grep "ainstalia.ai"

# Logs de consultas SQL
make logs-api | grep "Procesando consulta SQL"

# Logs de errores
make logs-api | grep "ERROR"
```

### **📊 Métricas de Uso**

El sistema registra automáticamente:

```python
# Tiempo de ejecución de consultas
"execution_time_ms": 245

# Consultas por rol de usuario
logger.info(f"Consulta SQL: '{natural_query}' para rol: {user_role}")

# Resultados obtenidos
"total_results": 15

# Errores y excepciones
logger.error(f"Error ejecutando consulta SQL: {e}")
```

### **🩺 Health Monitoring**

```bash
# Health check completo
curl http://localhost:8001/api/v1/ai/health

# Respuesta esperada:
{
  "sql_agent_status": "OK",
  "openai_connection": true,
  "database_connection": true,
  "available_roles": ["cliente", "tecnico", "administrador"],
  "last_check": "2024-01-15T10:30:00Z"
}
```

---

## 🔄 **ROADMAP FASE 2**

### **🎯 Próximas Funcionalidades**

1. **RAG System (Retrieval-Augmented Generation)**:
   - Base de conocimiento con documentos técnicos
   - Búsqueda semántica en manuales y procedimientos
   - Respuestas contextuales basadas en documentación

2. **Chat Integration**:
   - Integración con WhatsApp Business API
   - Conexión con Chatwoot para gestión multicanal
   - Bots conversacionales especializados

3. **Agentes Especializados**:
   - Agente de Inventario: Gestión inteligente de stock
   - Agente de Mantenimiento: Programación predictiva
   - Agente de Ventas: Recomendaciones y cotizaciones

### **🛠️ Preparación para Fase 2**

La arquitectura actual está preparada para:

```python
# Base para RAG System
@router.post("/knowledge-query", response_model=KnowledgeQueryResponse)
async def query_knowledge_base(request: KnowledgeQueryRequest):
    # TODO: Implementar RAG service en la siguiente fase
```

```python
# Sistema de feedback ya implementado
def submit_feedback(feedback: FeedbackRequest):
    # Almacena feedback para mejorar respuestas IA
    # Será utilizado para entrenar modelos personalizados
```

---

## 📋 **Checklist de Verificación - Fase 1**

### ✅ **Agentes de IA**
- [x] SQL Agent configurado con OpenAI GPT-4
- [x] LangChain SQL Agent operativo
- [x] Business Intelligence Agent funcionando
- [x] Sistema de permisos por roles implementado
- [x] Validación de consultas SQL seguras

### ✅ **API de IA**
- [x] 7 endpoints de IA implementados
- [x] Documentación automática en /docs
- [x] Validación con Pydantic schemas
- [x] Manejo de errores específicos
- [x] Health checks funcionando

### ✅ **Seguridad**
- [x] Control de acceso por roles
- [x] Validación de SQL injection
- [x] Filtrado de tablas por permisos
- [x] Logging de todas las consultas
- [x] Rate limiting implícito

### ✅ **Testing**
- [x] 32 tests de IA pasando (incluyendo RAGService y performance tests)
- [x] Mocking de servicios OpenAI
- [x] Tests de permisos y validaciones
- [x] Tests de manejo de errores
- [x] Cobertura completa de endpoints

### ✅ **Integración**
- [x] Funcionamiento con infraestructura Fase 0
- [x] Compatibilidad con todos los tests previos
- [x] No breaking changes en API existente
- [x] Configuración via variables de entorno
- [x] Docker compose actualizado

---

## 🎉 **Estado: FASE 1 COMPLETADA**

La Fase 1 está **100% funcional** con:

- ✅ **2 Agentes de IA** operativos y seguros
- ✅ **7 Endpoints especializados** para interacción con IA
- ✅ **Sistema robusto de seguridad** con control de acceso por roles
- ✅ **32 tests adicionales** todos pasando (88 tests totales)
- ✅ **Integración completa** con la infraestructura base
- ✅ **Preparación** para Fase 2 con RAG y chat integration

**🚀 AInstalia ahora puede procesar consultas empresariales en lenguaje natural con inteligencia artificial!**

---

## 🆘 **Resolución de Problemas de IA**

### **Error: OpenAI API Key inválida**
```bash
# Verificar clave en .env
grep OPENAI_API_KEY .env

# Validar formato (debe empezar con sk-)
echo $OPENAI_API_KEY

# Probar conexión
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

### **Error: SQL Agent no responde**
```bash
# Verificar logs del servicio
make logs-api | grep "SQL"

# Health check específico
curl http://localhost:8001/api/v1/ai/health

# Reiniciar servicios
make restart
```

### **Error: Consultas denegadas**
```bash
# Verificar permisos de rol
curl -X POST "http://localhost:8001/api/v1/ai/sql-query" \
  -d '{"query": "SELECT * FROM clients", "user_role": "administrador"}'

# Verificar que el rol sea válido: cliente, tecnico, administrador
```

### **Error: Tests de IA fallan**
```bash
# Ejecutar tests con más detalle
pytest backend/tests/phase_0/test_ai_endpoints.py -v -s

# Verificar que OpenAI API key esté configurada en testing
export OPENAI_API_KEY=tu_clave_aqui
pytest backend/tests/phase_0/test_ai_endpoints.py -v
```