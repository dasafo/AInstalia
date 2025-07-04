# 🧭 Roadmap Proyecto AI Support Assistant para Empresas Técnicas

Este proyecto busca construir una infraestructura profesional de atención al cliente para empresas técnicas (mantenimiento industrial, instaladores, etc.), basada en IA, canales conversacionales y automatización total.

---

## ✅ Fase 0 – Fundamentos y visión

- Definición del producto y casos de uso.
- Elección de tecnologías base: FastAPI, PostgreSQL, `n8n`, MCP, Docker.
- Estructuración inicial del backend: endpoints `/procesar`, `/estado`, `/consultar`.
- Inicio de portafolio para visibilidad profesional.
- Creación del repo `AInstalia`.

---

## ✅ Fase 1 – Backend funcional + MVP IA

- Creación de backend en FastAPI.
- Integración con PostgreSQL (`consultas_ia`, `estado_usuario`).
- Recepción de mensajes desde `n8n`.
- Clasificación del mensaje, ejecución de tarea (resumen, traducción, etc.).
- Persistencia y trazabilidad de todas las interacciones.

---

## 🚧 Fase 2 – Integración con Chatwoot + Telegram + n8n

### Objetivo:
Crear un flujo de comunicación real entre un cliente por Telegram y el backend IA, gestionado por Chatwoot como centro de operaciones.

### Tareas:

1. **Desplegar Chatwoot (self-hosted con Docker):**
   - Chatwoot + PostgreSQL + Redis en contenedor
   - Configuración de dominio, admin y seguridad

2. **Integrar Telegram:**
   - Crear bot con `@BotFather`
   - Añadir inbox tipo Telegram en Chatwoot
   - Confirmar recepción de mensajes

3. **Integrar con `n8n`:**
   - Activar Webhooks en Chatwoot (message_created)
   - Crear flujo en n8n: Trigger → análisis → respuesta IA
   - Responder al usuario por Telegram vía Chatwoot o directamente

4. **IA operativa en backend:**
   - Reutilización de endpoints
   - Respuestas adaptadas al rol (cliente, técnico, administrativo)

5. **Pruebas internas:**
   - Conversación simulada entre usuario y agente IA
   - Revisión de trazabilidad en Chatwoot y PostgreSQL

---

## 🧠 Fase 3 – Flujo de onboarding inteligente y validación de usuarios

- Detectar si un usuario es cliente o no.
- Flujo de onboarding para nuevos usuarios (pedir datos, zona, interés).
- Guardar estado en tabla `estado_usuario`.
- Interfaz básica de CRM para ver perfiles desde Chatwoot o panel externo.

---

## 📲 Fase 4 – WhatsApp Business (Twilio u otro proveedor)

- Crear cuenta verificada con número propio.
- Conectar canal WhatsApp Business a Chatwoot.
- Replicar flujos de Telegram, adaptados a restricciones de WhatsApp.
- Monitorear límites de sesión (24h), plantillas aprobadas, etc.

---

## 🧠 Fase 5 – Autoaprendizaje, feedback y mejora continua

- Añadir feedback del usuario ("¿Fue útil esta respuesta?").
- Entrenar al sistema con logs anteriores.
- Implementar `consultas frecuentes` o `autocompletado semántico`.
- Conectar RAG con documentos técnicos (Google Drive u otra fuente).
- Agente IA que consulta datos anteriores y aprende con correcciones humanas.

---

## 🧑‍💼 Fase 6 – Panel de administración para empresas clientes

- Multicliente: cada empresa con su configuración y técnicos
- Permisos: admins, operarios, agentes IA, soporte
- Estadísticas de uso, satisfacción y eficacia
- Posible modelo SaaS por cliente o por conversación

---

## 🔒 Fase 7 – Seguridad, escalabilidad y despliegue profesional

- HTTPS, backups automáticos, monitorización
- Control de errores (Sentry, logs centralizados)
- Despliegue con CI/CD en VPS, Railway o similar
- Documentación para réplica o venta del sistema

---

## 📌 Notas finales

- Canal de entrada: **Telegram** por ahora (sin fricciones)
- **Chatwoot en contenedor** da acceso a todas las funcionalidades pro
- WhatsApp se planifica para más adelante por complejidad/limitación
- `n8n` orquesta la lógica entre canales y backend IA
