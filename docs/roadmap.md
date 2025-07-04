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

## 🚧 **Fase 2: Comunicación Cliente - IA - Backend**

---

### 🔷 Objetivo general

Montar una infraestructura funcional donde:

* Un cliente (real o de prueba) contacta por Telegram
* Chatwoot recibe el mensaje en su interfaz web
* Se dispara un webhook hacia `n8n`
* `n8n` analiza el mensaje (por IA o lógica)
* Se responde automáticamente (desde IA o backend)
* Todo el historial queda registrado en Chatwoot

---

## 📦 Infraestructura técnica de esta fase

```
                👨 Cliente
                   │
            (mensaje por Telegram)
                   │
              🤖 Telegram Bot
                   │
           🔄 Chatwoot (Docker)
                   │
     📡 Webhook → n8n (Docker o Cloud)
                   │
         🧠 Backend IA (FastAPI / MCP)
                   │
            📨 Respuesta → Telegram
                   │
             🗂️ Chatwoot guarda todo
```

---

## 🔧 Componentes y tareas de la Fase 2

### 1. **Desplegar Chatwoot en Docker**

* `docker-compose.yml` con Chatwoot, PostgreSQL y Redis
* Crear admin y configuración inicial (dominio, mail, etc.)
* Verificar que esté accesible con HTTPS (vía NGINX o Caddy)

📁 Resultado: Interfaz profesional operativa

---

### 2. **Crear e integrar un Bot de Telegram**

* Crear bot con [@BotFather](https://t.me/botfather)
* Obtener `TOKEN` del bot
* Crear un inbox en Chatwoot del tipo **Telegram**
* Vincular el bot a Chatwoot

📁 Resultado: Mensajes que se envían al bot llegan a Chatwoot

---

### 3. **Activar Webhook de entrada en Chatwoot**

* Configurar en Chatwoot → Settings → Account → Webhooks
* Activar eventos `message_created` y `conversation_created`
* Apuntar al webhook que crearemos en `n8n`

📁 Resultado: Cada nuevo mensaje dispara una llamada a `n8n`

---

### 4. **Crear flujo de automatización en `n8n`**

* `Trigger`: Webhook desde Chatwoot
* `Node`: Procesar mensaje, detectar intención/rol
* `Node`: Llamada a backend IA (resumen, clasificación, decisión)
* `Node`: Responder al cliente usando **Chatwoot API o Telegram API**

📁 Resultado: Respuestas automáticas por IA desde Telegram o Chatwoot

---

### 5. **Backend IA (ya tienes parte hecho)**

* Endpoint tipo: `/procesar`
* Entrada: `message`, `sender`, `metadata`
* Salida: `respuesta`, `accion`, `logs`
* Opcional: Guardar en PostgreSQL

📁 Resultado: Puedes delegar lógica IA o workflow a FastAPI (ya tienes una base montada)

---

### 6. **Panel de soporte para pruebas**

* Usuario prueba (cliente) escribe en Telegram
* Tú ves el mensaje en Chatwoot
* La IA responde automáticamente, pero tú puedes intervenir manualmente
* Todo queda registrado

---

## 🧪 Bonus opcional: pruebas para rol cliente vs no cliente

* Si `sender` está en tu base de datos (clientes): flujo A
* Si no: flujo B (respuesta de onboarding o formulario)

---
