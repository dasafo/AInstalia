# 🚀 Guía de Instalación - Fase 0: Infraestructura Base

## ✅ Estado Actual

La **Fase 0** está **COMPLETA** y lista para usar. Tienes toda la infraestructura base configurada:

### 📁 Archivos creados:
- ✅ `requirements.txt` - Dependencias Python
- ✅ `docker-compose.yml` - Configuración Docker con PostgreSQL + PgAdmin
- ✅ `Dockerfile` - Imagen de la aplicación FastAPI
- ✅ `alembic.ini` - Configuración de migraciones
- ✅ `.env.example` - Plantilla de variables de entorno
- ✅ `.gitignore` - Archivos a ignorar en Git
- ✅ `scripts/load_data.py` - Script para cargar datos CSV
- ✅ `Makefile` - 40+ comandos para gestión completa

### 📊 Infraestructura disponible:
- ✅ **PostgreSQL** configurado en Docker
- ✅ **PgAdmin** para gestión gráfica de la base de datos
- ✅ **FastAPI** con estructura modular
- ✅ **SQLAlchemy** + Alembic para ORM y migraciones
- ✅ **Datos CSV** listos para cargar (46 clientes, 150 productos, etc.)
- ✅ **Script SQL** con 13 tablas completas

## 🔧 Pasos para ejecutar la Fase 0

### 1. **Preparar entorno**
```bash
# Clonar/estar en el directorio del proyecto
cd AInstalia

# Crear archivo .env basado en .env.example
cp .env.example .env
# o usando el Makefile:
make setup-env

# Editar .env con tus configuraciones reales (opcional)
nano .env
```

### 2. **Ejecutar con Docker (recomendado)**
```bash
# 🐳 Con Docker NO necesitas instalar Python ni crear entorno virtual
# Todo está containerizado

# Construir y ejecutar servicios
docker-compose up --build
# o usando el Makefile:
make up

# En otra terminal, verificar que todo funciona
curl http://localhost:8001/health
```

### 3. **Configurar PgAdmin**
```bash
# Abrir PgAdmin automáticamente
make pgadmin

# O manualmente ir a: http://localhost:5051
# Credenciales:
# Email: admin@ainstalia.com
# Password: admin123

# Ver instrucciones de configuración
make setup-pgadmin
```

### 4. **Verificar base de datos**
```bash
# Opción 1: Conectar por línea de comandos
make shell-db

# Verificar tablas creadas
\dt

# Ver datos de ejemplo
SELECT COUNT(*) FROM clients;
SELECT COUNT(*) FROM products;

# Opción 2: Usar PgAdmin (interfaz gráfica)
# Ir a http://localhost:5050 y seguir las instrucciones
```

### 5. **Cargar datos CSV (opcional)**
```bash
# Si quieres cargar los datos CSV adicionales
# Esto se ejecuta DENTRO del contenedor
make load-data
```

## 💡 **¿Cuándo SÍ necesitas entorno virtual?**

Solo si quieres desarrollar **fuera de Docker** (no recomendado para este proyecto):

```bash
# Solo para desarrollo local SIN Docker:
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

**Pero con nuestro setup de Docker, esto NO es necesario** ✅

## 🧪 Probar la API

Una vez ejecutando, puedes probar:

```bash
# Endpoint de salud
curl http://localhost:8001/health

# Documentación automática de FastAPI
http://localhost:8001/docs

# Endpoint raíz
curl http://localhost:8001/
```

## 🌐 URLs de servicios

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **FastAPI** | http://localhost:8001 | - |
| **API Docs** | http://localhost:8001/docs | - |
| **PgAdmin** | http://localhost:5051 | admin@ainstalia.com / admin123 |
| **PostgreSQL** | localhost:5433 | user / password |

## 🎛️ Configurar PgAdmin paso a paso

1. **Acceder a PgAdmin**: http://localhost:5051
2. **Login**:
   - Email: `admin@ainstalia.com`
   - Password: `admin123`
3. **Crear servidor**:
   - Click derecho en "Servers" → "Create" → "Server"
4. **Configuración**:
   - **General tab**:
     - Name: `AInstalia`
   - **Connection tab**:
     - Host: `postgres`
     - Port: `5432`
     - Database: `ainstalia_db`
     - Username: `user`
     - Password: `password`
5. **Guardar**: Click "Save"

¡Ya tienes acceso gráfico completo a la base de datos! 🎉

## 📋 Verificación de Fase 0 Completa

Confirma que tienes:

- [ ] ✅ PostgreSQL corriendo en puerto 5433
- [ ] ✅ PgAdmin corriendo en puerto 5051
- [ ] ✅ FastAPI corriendo en puerto 8001
- [ ] ✅ 13 tablas creadas en la base de datos
- [ ] ✅ PgAdmin conectado a PostgreSQL
- [ ] ✅ Datos CSV disponibles para cargar
- [ ] ✅ API respondiendo correctamente
- [ ] ✅ Documentación en /docs accesible

## 🎯 Próximos pasos

Una vez que la Fase 0 esté funcionando:

1. **Fase 1**: Crear endpoints CRUD para todas las tablas
2. **Fase 2**: Integrar mensajería (WhatsApp + Chatwoot)
3. **Fase 3**: Implementar agentes IA especializados

## 🚀 Comandos útiles del Makefile

```bash
# Comandos básicos
make help           # Ver todos los comandos
make up             # Levantar servicios
make down           # Bajar servicios
make status         # Ver estado de contenedores

# Base de datos
make shell-db       # Acceso a PostgreSQL
make load-data      # Cargar datos CSV
make check-data     # Verificar datos
make db-backup      # Crear backup

# PgAdmin
make pgadmin        # Abrir PgAdmin en navegador
make setup-pgadmin  # Ver instrucciones de configuración
make logs-pgadmin   # Ver logs de PgAdmin

# Desarrollo
make dev            # Modo desarrollo
make test-api       # Probar API
make quick-start    # Inicio rápido completo
```

## 🆘 Resolución de problemas

### Error de conexión a base de datos:
```bash
# Verificar que PostgreSQL está ejecutando
docker-compose ps

# Ver logs
docker-compose logs postgres
# o
make logs-db
```

### PgAdmin no carga:
```bash
# Verificar logs de PgAdmin
make logs-pgadmin

# Verificar que el puerto 5050 no esté ocupado
netstat -tlnp | grep 5050
```

### Error al instalar dependencias:
```bash
# Actualizar pip
pip install --upgrade pip

# Instalar con verbose para ver errores
pip install -v -r requirements.txt
```

### Puerto ocupado:
```bash
# Cambiar puertos en docker-compose.yml si están ocupados
# Ejemplo para cambiar PgAdmin de 5050 a 5051:
# "5051:80" en lugar de "5050:80"
```

---

¡La Fase 0 está lista! 🎉 Con esta infraestructura completa (PostgreSQL + PgAdmin + FastAPI + Makefile) puedes proceder a desarrollar las siguientes fases del sistema multiagente. 