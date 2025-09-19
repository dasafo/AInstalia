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

## 🚧 **Fase 2: Comunicación Cliente - IA - Backend (sin Chatwoot)**

---

### 🔷 Objetivo general

Montar una infraestructura funcional donde:

* Un cliente (real o de prueba) contacta por Telegram
* n8n recibe el mensaje mediante el nodo Telegram Trigger
* n8n analiza el mensaje (por IA o lógica)
* n8n llama al backend FastAPI para procesamiento avanzado
* Se responde automáticamente al cliente por Telegram
* Todo el historial queda registrado en la base de datos propia

---

## 📦 Infraestructura técnica de esta fase

```
                👨 Cliente
                   │
            (mensaje por Telegram)
                   │
              🤖 Telegram Bot
                   │
                🔄 n8n
                   │
         🧠 Backend IA (FastAPI / MCP)
                   │
            📨 Respuesta → Telegram
                   │
             🗂️ Historial en PostgreSQL
```

---

## 🔧 Componentes y tareas de la Fase 2

### 1. **Configurar el Bot de Telegram**

* Crear bot con [@BotFather](https://t.me/botfather)
* Obtener `TOKEN` del bot
* Configurar el nodo Telegram Trigger en n8n

📁 Resultado: Mensajes que se envían al bot llegan a n8n

---

### 2. **Crear flujo de automatización en `n8n`**

* `Trigger`: Telegram Trigger
* `Node`: Procesar mensaje, detectar intención/rol
* `Node`: Llamada a backend IA (resumen, clasificación, decisión)
* `Node`: Responder al cliente usando el nodo Telegram
* `Node`: Guardar historial en PostgreSQL (opcional)

📁 Resultado: Respuestas automáticas por IA desde Telegram

---

### 3. **Backend IA (FastAPI)**

* Endpoint tipo: `/procesar`
* Entrada: `message`, `sender`, `metadata`
* Salida: `respuesta`, `accion`, `logs`
* Opcional: Guardar en PostgreSQL

📁 Resultado: Puedes delegar lógica IA o workflow a FastAPI (ya tienes una base montada)

---

### 4. **Panel de soporte para pruebas**

* Usuario prueba (cliente) escribe en Telegram
* El flujo es 100% automatizado
* Todo queda registrado en la base de datos propia

---

## 🧪 Bonus opcional: pruebas para rol cliente vs no cliente

* Si `sender` está en tu base de datos (clientes): flujo A
* Si no: flujo B (respuesta de onboarding o formulario)

---
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
