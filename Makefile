# Makefile para AInstalia
# Proyecto de sistema multiagente para gestión empresarial con FastAPI

# Variables de configuración
COMPOSE_FILE := docker-compose.yml
PROJECT_NAME := ainstalia
BACKEND_CONTAINER := $(PROJECT_NAME)_backend
POSTGRES_CONTAINER := $(PROJECT_NAME)_postgres
PGADMIN_CONTAINER := $(PROJECT_NAME)_pgadmin

# Colores para output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color
BLUE := \033[0;34m

.PHONY: help build up down restart status logs clean test dev prod backup restore

# Comando por defecto
.DEFAULT_GOAL := help

## 🚀 Comandos principales
help: ## Mostrar esta ayuda
	@echo "$(GREEN)Makefile para AInstalia - Sistema Multiagente$(NC)"
	@echo "$(BLUE)======================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Uso: make [comando]$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

build: ## 🔨 Construir todos los contenedores
	@echo "$(YELLOW)🔨 Construyendo contenedores...$(NC)"
	docker compose -f $(COMPOSE_FILE) build

up: ## ⬆️ Levantar todos los servicios
	@echo "$(YELLOW)⬆️ Levantando servicios...$(NC)"
	docker compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Servicios levantados correctamente$(NC)"
	@echo "$(BLUE)📖 API Docs: http://localhost:8001/docs$(NC)"
	@echo "$(BLUE)🐘 PostgreSQL: http://localhost:5433$(NC)"
	@echo "$(BLUE)🎛️ PgAdmin: http://localhost:5050$(NC)"
	@echo "$(BLUE)   Email: admin@admin.com$(NC)"
	@echo "$(BLUE)   Password: admin$(NC)"
	@echo "$(BLUE)🤖 n8n Workflow: http://localhost:5678$(NC)"
	@echo "$(GREEN)============================================$(NC)"

down: ## ⬇️ Bajar todos los servicios
	@echo "$(YELLOW)⬇️ Bajando servicios...$(NC)"
	docker compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)✅ Servicios detenidos correctamente$(NC)"

restart: ## 🔄 Reiniciar todos los servicios
	@echo "$(YELLOW)🔄 Reiniciando servicios...$(NC)"
	docker compose -f $(COMPOSE_FILE) restart
	@echo "$(GREEN)✅ Servicios reiniciados correctamente$(NC)"

## 📊 Monitoreo y logs
status: ## 📊 Ver estado de contenedores
	@echo "$(YELLOW)📊 Estado de contenedores:$(NC)"
	docker compose -f $(COMPOSE_FILE) ps

logs: ## 📋 Ver logs de todos los servicios
	@echo "$(YELLOW)📋 Logs de todos los servicios:$(NC)"
	docker compose -f $(COMPOSE_FILE) logs --tail=50 -f

logs-backend: ## 📋 Ver logs del backend
	@echo "$(YELLOW)📋 Logs del backend:$(NC)"
	docker logs -f $(BACKEND_CONTAINER)

logs-db: ## 📋 Ver logs de PostgreSQL
	@echo "$(YELLOW)📋 Logs de PostgreSQL:$(NC)"
	docker logs -f $(POSTGRES_CONTAINER)

logs-pgadmin: ## 📋 Ver logs de PgAdmin
	@echo "$(YELLOW)📋 Logs de PgAdmin:$(NC)"
	docker logs -f $(PGADMIN_CONTAINER)

## 🔧 Desarrollo
dev: ## 🚀 Modo desarrollo (build + up + logs)
	@echo "$(YELLOW)🚀 Iniciando modo desarrollo...$(NC)"
	make build
	make up
	@echo "$(GREEN)✅ Entorno de desarrollo listo$(NC)"
	@echo "$(BLUE)🔍 Para ver logs: make logs$(NC)"

rebuild: ## 🔨 Reconstruir y levantar servicios
	@echo "$(YELLOW)🔨 Reconstruyendo servicios...$(NC)"
	docker compose -f $(COMPOSE_FILE) up -d --build
	@echo "$(GREEN)✅ Servicios reconstruidos y levantados$(NC)"

rebuild-backend: ## 🔨 Reconstruir solo el backend
	@echo "$(YELLOW)🔨 Reconstruyendo backend...$(NC)"
	docker compose -f $(COMPOSE_FILE) up -d --build backend
	@echo "$(GREEN)✅ Backend reconstruido$(NC)"

## 🔍 Debugging y acceso
shell-backend: ## 🐚 Acceso shell al contenedor backend
	@echo "$(YELLOW)🐚 Accediendo al contenedor backend...$(NC)"
	docker exec -it $(BACKEND_CONTAINER) /bin/bash

shell-db: ## 🐚 Acceso shell a PostgreSQL
	@echo "$(YELLOW)🐚 Accediendo a PostgreSQL...$(NC)"
	docker exec -it $(POSTGRES_CONTAINER) psql -U admin -d ainstalia_db

shell-pgadmin: ## 🐚 Acceso shell a PgAdmin
	@echo "$(YELLOW)🐚 Accediendo al contenedor PgAdmin...$(NC)"
	docker exec -it $(PGADMIN_CONTAINER) /bin/bash

## 🧹 Limpieza
clean: ## 🧹 Limpiar contenedores, imágenes y volúmenes
	@echo "$(YELLOW)🧹 Limpiando recursos Docker...$(NC)"
	docker compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker system prune -f
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

clean-all: ## 🧹 Limpieza completa (incluye imágenes)
	@echo "$(RED)⚠️ ATENCIÓN: Esto eliminará TODAS las imágenes Docker$(NC)"
	@read -p "¿Estás seguro? [y/N]: " confirm && [ "$$confirm" = "y" ]
	docker compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker system prune -a -f
	@echo "$(GREEN)✅ Limpieza completa realizada$(NC)"

## 🧪 Testing y verificación
test-api: ## 🧪 Probar endpoints básicos de la API
	@echo "$(YELLOW)🧪 Probando endpoints de la API...$(NC)"
	@echo "$(BLUE)🔍 Health check:$(NC)"
	curl -s http://localhost:8001/ | jq . || echo "API no disponible"
	@echo "\n$(BLUE)👥 Clientes:$(NC)"
	curl -s http://localhost:8001/api/v1/clients/?limit=3 | jq '.[:3]' || echo "Endpoint de clientes no disponible"
	@echo "\n$(BLUE)📦 Productos:$(NC)"
	curl -s http://localhost:8001/api/v1/products/?limit=3 | jq '.[:3]' || echo "Endpoint de productos no disponible"

check-health: ## 🏥 Verificar salud de todos los servicios
	@echo "$(YELLOW)🏥 Verificando salud de servicios...$(NC)"
	@echo "$(BLUE)Backend:$(NC)"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8001/ || echo "❌ Backend no responde"
	@echo "$(BLUE)PostgreSQL:$(NC)"
	@docker exec $(POSTGRES_CONTAINER) pg_isready -U admin -d ainstalia_db && echo "✅ PostgreSQL OK" || echo "❌ PostgreSQL no responde"
	@echo "$(BLUE)PgAdmin:$(NC)"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:5051/ && echo "✅ PgAdmin OK" || echo "❌ PgAdmin no responde"

## 📊 Información del sistema
info: ## 📊 Mostrar información del proyecto
	@echo "$(GREEN)📊 Información del Proyecto AInstalia$(NC)"
	@echo "$(BLUE)===============================================$(NC)"
	@echo "Proyecto: $(PROJECT_NAME)"
	@echo "Compose File: $(COMPOSE_FILE)"
	@echo ""
	@echo "$(YELLOW)🔗 URLs de Servicios:$(NC)"
	@echo "  • API Backend: http://localhost:8001"
	@echo "  • API Docs: http://localhost:8001/docs"
	@echo "  • PostgreSQL: http://localhost:5433"
	@echo "  • PgAdmin: http://localhost:5050"
	@echo "  • n8n Workflow: http://localhost:${N8N_PORT}"
	@echo ""
	@echo "$(YELLOW)📦 Contenedores:$(NC)"
	@echo "  • Backend: $(BACKEND_CONTAINER)"
	@echo "  • PostgreSQL: $(POSTGRES_CONTAINER)"
	@echo "  • PgAdmin: $(PGADMIN_CONTAINER)"
	@echo "  • n8n: $(N8N_CONTAINER)"
	@echo ""
	@echo "$(YELLOW)🔑 Credenciales PgAdmin:$(NC)"
	@echo "  • Email: admin@admin.com"
	@echo "  • Password: admin"

## 🗃️ Base de datos
db-backup: ## 💾 Backup de la base de datos
	@echo "$(YELLOW)💾 Creando backup de la base de datos...$(NC)"
	@mkdir -p backups
	docker exec $(POSTGRES_CONTAINER) pg_dump -U admin ainstalia_db > backups/ainstalia_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Backup creado en backups/$(NC)"

db-restore: ## 📥 Restaurar base de datos (requiere archivo)
	@echo "$(YELLOW)📥 Restaurando base de datos...$(NC)"
	@echo "$(RED)Uso: make db-restore FILE=backups/archivo.sql$(NC)"
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)❌ Error: Especifica el archivo con FILE=ruta/archivo.sql$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f "$(FILE)" ]; then \
		echo "$(RED)❌ Error: Archivo $(FILE) no encontrado$(NC)"; \
		exit 1; \
	fi
	docker exec -i $(POSTGRES_CONTAINER) psql -U admin ainstalia_db < $(FILE)
	@echo "$(GREEN)✅ Base de datos restaurada$(NC)"

db-reset: ## 🔄 Reiniciar base de datos (recrear todas las tablas)
	@echo "$(RED)⚠️ ATENCIÓN: Esto eliminará TODOS los datos$(NC)"
	@read -p "¿Estás seguro? [y/N]: " confirm && [ "$$confirm" = "y" ]
	@echo "$(YELLOW)🔄 Reiniciando base de datos...$(NC)"
	docker exec -i $(POSTGRES_CONTAINER) psql -U admin ainstalia_db < data/create_tables.sql
	@echo "$(GREEN)✅ Base de datos reiniciada$(NC)"

## 📊 Datos
load-data: ## 📊 Cargar datos CSV a la base de datos
	@echo "$(YELLOW)📊 Cargando datos CSV...$(NC)"
	python scripts/load_data.py
	@echo "$(GREEN)✅ Datos cargados correctamente$(NC)"

check-data: ## 🔍 Verificar datos en la base de datos
	@echo "$(YELLOW)🔍 Verificando datos en la base de datos...$(NC)"
	@docker exec $(POSTGRES_CONTAINER) psql -U admin ainstalia_db -c "\
		SELECT 'clients' as tabla, count(*) as registros FROM clients UNION ALL \
		SELECT 'products', count(*) FROM products UNION ALL \
		SELECT 'technicians', count(*) FROM technicians UNION ALL \
		SELECT 'warehouses', count(*) FROM warehouses UNION ALL \
		SELECT 'installed_equipment', count(*) FROM installed_equipment UNION ALL \
		SELECT 'interventions', count(*) FROM interventions UNION ALL \
		SELECT 'contracts', count(*) FROM contracts UNION ALL \
		SELECT 'orders', count(*) FROM orders UNION ALL \
		SELECT 'order_items', count(*) FROM order_items UNION ALL \
		SELECT 'stock', count(*) FROM stock UNION ALL \
		SELECT 'knowledge_feedback', count(*) FROM knowledge_feedback UNION ALL \
		SELECT 'chat_sessions', count(*) FROM chat_sessions UNION ALL \
		SELECT 'chat_messages', count(*) FROM chat_messages;"

## 🚀 Entornos
prod: ## 🚀 Levantar en modo producción
	@echo "$(YELLOW)🚀 Levantando en modo producción...$(NC)"
	docker compose -f $(COMPOSE_FILE) up -d --build
	@echo "$(GREEN)✅ Entorno de producción levantado$(NC)"

## 📈 Monitoreo avanzado
watch-logs: ## 👀 Monitorear logs en tiempo real (filtrado)
	@echo "$(YELLOW)👀 Monitoreando logs (Ctrl+C para salir)...$(NC)"
	docker compose -f $(COMPOSE_FILE) logs -f | grep -E "(ERROR|WARNING|INFO|Started|Stopped)"

stats: ## 📈 Estadísticas de contenedores
	@echo "$(YELLOW)📈 Estadísticas de contenedores:$(NC)"
	docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

## 🔧 Utilidades
update: ## 🔄 Actualizar imágenes base
	@echo "$(YELLOW)🔄 Actualizando imágenes base...$(NC)"
	docker compose -f $(COMPOSE_FILE) pull
	@echo "$(GREEN)✅ Imágenes actualizadas$(NC)"

ports: ## 🌐 Mostrar puertos utilizados
	@echo "$(YELLOW)🌐 Puertos utilizados por el proyecto:$(NC)"
	@echo "$(BLUE)AInstalia:$(NC)"
	@echo "  • 8000 - FastAPI Backend"
	@echo "  • 5432 - PostgreSQL"
	@echo "  • 5050 - PgAdmin"
	@echo "  • ${N8N_PORT} - n8n Workflow Automation"
	@echo "  • 6379 - Redis"


## 📚 Documentación
docs: ## 📚 Abrir documentación de la API
	@echo "$(YELLOW)📚 Abriendo documentación de la API...$(NC)"
	@command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:8001/docs || \
	command -v open >/dev/null 2>&1 && open http://localhost:8001/docs || \
	echo "$(BLUE)📖 Visita: http://localhost:8001/docs$(NC)"

pgadmin: ## 🎛️ Abrir PgAdmin en el navegador
	@echo "$(YELLOW)🎛️ Abriendo PgAdmin...$(NC)"
	@command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:5051 || \
	command -v open >/dev/null 2>&1 && open http://localhost:5051 || \
	echo "$(BLUE)🎛️ Visita: http://localhost:5051$(NC)"
	@echo "$(BLUE)📧 Email: admin@admin.com$(NC)"
	@echo "$(BLUE)🔑 Password: admin$(NC)"

## 🎯 Comandos rápidos
quick-start: ## ⚡ Inicio rápido AInstalia (clean + build + up)
	@echo "$(YELLOW)⚡ Inicio rápido de AInstalia...$(NC)"
	make clean
	make build
	make up
	@echo "$(GREEN)✅ AInstalia iniciado correctamente$(NC)"
	@echo "$(BLUE)🔍 Verifica el estado con: make status$(NC)"

quick-start-full: ## ⚡ Inicio rápido completo (AInstalia)
	@echo "$(YELLOW)⚡ Inicio rápido completo (AInstalia)...$(NC)"
	make clean
	make build
	make up
	@echo "$(GREEN)✅ Sistema completo iniciado$(NC)"
	@echo "$(BLUE)💼 AInstalia: http://localhost:8000$(NC)"
	@echo "$(BLUE)🔍 Verifica el estado con: make status$(NC)"

quick-test: ## ⚡ Prueba rápida completa (up + test + data)
	@echo "$(YELLOW)⚡ Prueba rápida completa...$(NC)"
	make up
	sleep 10
	make test-api
	make check-data
	@echo "$(GREEN)✅ Prueba completa finalizada$(NC)"

stop-all: ## ⏹️ Parar todos los contenedores de Docker
	@echo "$(YELLOW)⏹️ Parando todos los contenedores de Docker...$(NC)"
	docker stop $$(docker ps -q) 2>/dev/null || echo "No hay contenedores ejecutándose"
	@echo "$(GREEN)✅ Todos los contenedores detenidos$(NC)"

## 🧪 Testing y desarrollo
install-deps: ## 📦 Instalar dependencias localmente
	@echo "$(YELLOW)📦 Instalando dependencias localmente...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)✅ Dependencias instaladas$(NC)"

format: ## 🎨 Formatear código con black
	@echo "$(YELLOW)🎨 Formateando código...$(NC)"
	black backend/ scripts/
	@echo "$(GREEN)✅ Código formateado$(NC)"

lint: ## 🔍 Verificar código con flake8
	@echo "$(YELLOW)🔍 Verificando código...$(NC)"
	flake8 backend/ scripts/
	@echo "$(GREEN)✅ Código verificado$(NC)"

## 🤖 Comandos específicos de AInstalia
init-db: ## 🗃️ Inicializar base de datos (crear tablas + cargar datos)
	@echo "$(YELLOW)🗃️ Inicializando base de datos...$(NC)"
	make up
	sleep 5
	make load-data
	@echo "$(GREEN)✅ Base de datos inicializada con datos$(NC)"
	@echo "$(BLUE)🎛️ Accede a PgAdmin: http://localhost:5050$(NC)"

agents-test: ## 🤖 Probar agentes IA (cuando estén implementados)
	@echo "$(YELLOW)🤖 Probando agentes IA...$(NC)"
	@echo "$(BLUE)🔮 Funcionalidad pendiente de implementar$(NC)"

whatsapp-test: ## 📱 Probar integración WhatsApp (cuando esté implementada)
	@echo "$(YELLOW)📱 Probando integración WhatsApp...$(NC)"
	@echo "$(BLUE)🔮 Funcionalidad pendiente de implementar$(NC)"



## 🔄 n8n Automation
N8N_CONTAINER := $(PROJECT_NAME)_n8n

n8n-open: ## 🌐 Abrir n8n en el navegador
	@echo "$(YELLOW)🌐 Abriendo n8n...$(NC)"
	@command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:$(N8N_PORT) || \
	command -v open >/dev/null 2>&1 && open http://localhost:$(N8N_PORT) || \
	echo "$(BLUE)🤖 Visita: http://localhost:$(N8N_PORT)$(NC)"
	@echo "$(BLUE)   Para login, usa las credenciales configuradas en .env (N8N_BASIC_AUTH_USER, N8N_BASIC_AUTH_PASSWORD)$(NC)"

logs-n8n: ## 📋 Ver logs de n8n
	@echo "$(YELLOW)📋 Logs de n8n:$(NC)"
	docker logs -f $(N8N_CONTAINER)

## 🔧 Configuración de entorno
setup-env: ## ⚙️ Configurar archivo .env desde .env.example
	@echo "$(YELLOW)⚙️ Configurando archivo .env...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✅ Archivo .env creado desde .env.example$(NC)"; \
		echo "$(BLUE)📝 Edita .env con tus configuraciones reales$(NC)"; \
	else \
		echo "$(YELLOW)⚠️ El archivo .env ya existe$(NC)"; \
	fi

setup-pgadmin: ## 🎛️ Configurar conexión de PgAdmin a PostgreSQL
	@echo "$(YELLOW)🎛️ Configurando PgAdmin...$(NC)"
	@echo "$(BLUE)📋 Pasos para conectar PgAdmin a PostgreSQL:$(NC)"
	@echo "$(GREEN)1.$(NC) Abre http://localhost:5051"
	@echo "$(GREEN)2.$(NC) Login: admin@admin.com / admin"
	@echo "$(GREEN)3.$(NC) Click derecho en 'Servers' → Create → Server"
	@echo "$(GREEN)4.$(NC) General tab → Name: AInstalia"
	@echo "$(GREEN)5.$(NC) Connection tab:"
	@echo "   • Host: postgres"
	@echo "   • Port: 5432"
	@echo "   • Database: ainstalia_db"
	@echo "   • Username: user"
	@echo "   • Password: password"
	@echo "$(GREEN)6.$(NC) Click 'Save'" 