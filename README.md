# 🚀 AInstalia - Sistema de Gestión Industrial con IA

**AInstalia** es un sistema completo de gestión para empresas de mantenimiento industrial que integra múltiples agentes de IA especializados para automatizar procesos empresariales críticos.

## 📋 Descripción del Proyecto

AInstalia combina una **API REST robusta** con **agentes de IA especializados** para ofrecer:

- 🔍 **Consultas SQL en lenguaje natural** - Pregunta datos empresariales en español
- 📊 **Insights automáticos de negocio** - Análisis inteligente de KPIs
- 🛠️ **Gestión completa de inventario** - Control de stock, productos y almacenes
- 👥 **Administración de clientes** - CRM integrado con historial completo
- 🔧 **Gestión de intervenciones técnicas** - Seguimiento de mantenimientos
- 💬 **Base de conocimiento** - Sistema de feedback para mejora continua

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    🤖 AGENTES IA ESPECIALIZADOS             │
│   SQL Agent | Business Intelligence | Knowledge Base       │
├─────────────────────────────────────────────────────────────┤
│                    🌐 API REST (FastAPI)                    │
│   Endpoints CRUD | Validaciones | Documentación Auto       │
├─────────────────────────────────────────────────────────────┤
│                📋 CAPA DE LÓGICA (CRUD + Schemas)          │
│   Operaciones de Negocio | Validaciones Pydantic          │
├─────────────────────────────────────────────────────────────┤
│                📊 MODELOS DE DATOS (SQLAlchemy)            │
│   ORM | Relaciones | Migraciones Alembic                  │
├─────────────────────────────────────────────────────────────┤
│                🗄️  BASE DE DATOS (PostgreSQL)              │
│   13 Tablas | Integridad Referencial | Índices            │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Características Principales

### 🤖 **Agentes de IA Integrados**
- **SQL Agent**: Convierte preguntas en español a consultas SQL seguras
- **Business Intelligence**: Genera insights automáticos del negocio
- **Knowledge Base**: Sistema de feedback para mejora continua

### 🛡️ **Seguridad y Permisos**
- **Control de acceso por roles**: Cliente, Técnico, Administrador
- **Validación de consultas SQL**: Solo operaciones de lectura permitidas
- **Filtrado automático**: Acceso limitado según permisos de usuario

### 📊 **Gestión Empresarial Completa**
- **Clientes**: CRM con historial completo de interacciones
- **Inventario**: Control de stock, productos y almacenes
- **Técnicos**: Gestión de personal y asignaciones
- **Intervenciones**: Seguimiento de mantenimientos y reparaciones
- **Contratos**: Administración de acuerdos de servicio
- **Pedidos**: Sistema completo de órdenes de compra

## 🚀 Estados de Desarrollo

| Fase | Estado | Descripción |
|------|--------|-------------|
| **Fase 0** | ✅ **COMPLETA** | Infraestructura base + API CRUD |
| **Fase 1** | ✅ **COMPLETA** | Agentes IA + SQL en lenguaje natural |
| **Fase 2** | 🔄 **Planificada** | Integración WhatsApp + Chatwoot |
| **Fase 3** | 🔄 **Planificada** | Agentes especializados por dominio |

## 🛠️ Tecnologías Utilizadas

### **Backend**
- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para Python con soporte async
- **PostgreSQL**: Base de datos relacional robusta
- **Alembic**: Migraciones de base de datos
- **Pydantic**: Validación de datos y schemas

### **IA y Machine Learning**
- **OpenAI GPT-4**: Modelo de lenguaje para comprensión natural
- **LangChain**: Framework para aplicaciones con LLM
- **SQL Agent**: Agente especializado en consultas de base de datos

### **DevOps y Desarrollo**
- **Docker**: Containerización completa del stack
- **PgAdmin**: Interfaz gráfica para PostgreSQL
- **pytest**: Framework de testing automatizado
- **Makefile**: Automatización de tareas de desarrollo

## 🚀 Instalación y Configuración

### **Requisitos Previos**
- Docker y Docker Compose
- Git
- Clave API de OpenAI (para funcionalidades de IA)

### **Instalación Rápida**

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd AInstalia

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu clave de OpenAI

# 3. Levantar todos los servicios
make up

# 4. Verificar instalación
make test-api
```

### **Acceso a Servicios**

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **API REST** | http://localhost:8001 | - |
| **Documentación API** | http://localhost:8001/docs | - |
| **PgAdmin** | http://localhost:5051 | admin@ainstalia.com / admin123 |
| **PostgreSQL** | localhost:5433 | user / password |

## 📖 Documentación Detallada

- 📚 **[README_FASE_0.md](./README_FASE_0.md)** - Infraestructura base y API CRUD
- 🤖 **[README_FASE_1.md](./README_FASE_1.md)** - Implementación de agentes IA
- 🔄 **README_FASE_2.md** - Integración de mensajería (próximamente)

## 🧪 Testing

El proyecto incluye una suite completa de tests automatizados:

```bash
# Ejecutar todos los tests
make test

# Tests específicos
make test-phase-0    # Tests de infraestructura
make test-phase-1    # Tests de agentes IA

# Tests con coverage
make test-coverage
```

**Cobertura actual**: 73 tests pasando ✅

## 🎯 Ejemplos de Uso

### **Consultas SQL en Lenguaje Natural**

```bash
# Consulta usando curl
curl -X POST "http://localhost:8001/api/v1/ai/sql-query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuántos clientes tenemos en total?",
    "user_role": "administrador",
    "include_sql": true
  }'

# Respuesta:
{
  "success": true,
  "result": [{"total": 25}],
  "sql_query": "SELECT COUNT(*) as total FROM clients",
  "execution_time_ms": 150
}
```

### **Insights Automáticos de Negocio**

```bash
curl "http://localhost:8001/api/v1/ai/insights?user_role=administrador"

# Respuesta:
{
  "success": true,
  "insights": {
    "total_clientes": [{"total": 25}],
    "ordenes_pendientes": [{"total": 8}],
    "stock_bajo": [{"total": 12}]
  }
}
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit los cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- 📧 Email: support@ainstalia.com
- 📖 Documentación: `/docs` endpoint de la API
- 🐛 Issues: Crear un issue en el repositorio

---

**Desarrollado con ❤️ para automatizar la gestión industrial con IA**
