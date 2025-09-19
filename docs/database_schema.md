# Documentación Completa de la Base de Datos - AInstalia

## Descripción General

La base de datos `ainstalia_db` contiene **DOS SISTEMAS INTEGRADOS**:

1. **Sistema de Negocio AInstalia** (14 tablas) - Gestión de clientes, productos, servicios técnicos, inventario y comunicaciones
2. **Sistema n8n** (~35 tablas) - Automatización de workflows, credenciales, ejecuciones y logs

**Total: ~49 tablas** (esto es completamente normal y esperado)

## Arquitectura y Lógica del Negocio

### **Flujos Principales del Sistema AInstalia:**

1. **📱 Flujo Telegram → Agentes IA**:
   ```
   Usuario Telegram → Router → Agente específico → Respuesta
   ```

2. **🏢 Gestión Comercial**:
   ```
   Cliente → Pedido → Productos → Instalación → Mantenimiento
   ```

3. **🔧 Gestión Técnica**:
   ```
   Equipo instalado → Intervenciones → Historial → Contratos
   ```

4. **📦 Gestión Inventario**:
   ```
   Productos → Stock por almacén → Pedidos → Instalaciones
   ```

---

# TABLAS DEL SISTEMA AINSTALIA (14 tablas)

## 1. Tabla: `usuarios` ⭐ **NUEVA - INTEGRACIÓN TELEGRAM**
**Propósito**: Gestión unificada de usuarios del sistema con soporte para Telegram Bot.

```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL,
    email VARCHAR UNIQUE,
    telefono VARCHAR,
    empresa VARCHAR,
    ciudad VARCHAR,
    rol VARCHAR DEFAULT 'cliente' CHECK (rol IN ('cliente', 'administrador', 'tecnico')),
    telegram_user_id BIGINT UNIQUE,
    telegram_username VARCHAR,
    activo BOOLEAN DEFAULT true,
    fecha_registro TIMESTAMP DEFAULT now(),
    ultima_actividad TIMESTAMP DEFAULT now()
);
```

**Campos Detallados**:
- `id`: Identificador único interno del sistema
- `nombre`: Nombre completo del usuario (obligatorio)
- `email`: Email único (usado para login web y notificaciones)
- `telefono`: Teléfono de contacto
- `empresa`: Empresa donde trabaja (para contexto comercial)
- `ciudad`: Ubicación geográfica (para asignación de técnicos)
- `rol`: Define permisos y funcionalidades:
  - **'cliente'**: Acceso a agente cliente (consultas, pedidos, soporte)
  - **'administrador'**: Acceso a agente administrativo (reportes, gestión)
  - **'tecnico'**: Acceso limitado (principalmente para reportar intervenciones)
- `telegram_user_id`: ID único de Telegram (vincula chat con usuario)
- `telegram_username`: Username de Telegram (@usuario)
- `activo`: Estado del usuario (permite suspender acceso)
- `fecha_registro`: Cuándo se registró en el sistema
- `ultima_actividad`: Última interacción (actualizada por el router)

**Relaciones**:
- **Con `telegram_interactions`**: Un usuario puede tener múltiples interacciones
- **Migra datos de `clients`**: Los clientes existentes se convierten en usuarios
- **Usado por**: Router de Telegram para enrutamiento de conversaciones

**Lógica de Negocio**:
```
Usuario Telegram → Verificar en tabla usuarios → Determinar rol → Dirigir al agente correcto
```

---

## 2. Tabla: `telegram_interactions` ⭐ **NUEVA - LOGS TELEGRAM**
**Propósito**: Registro completo de todas las interacciones del bot de Telegram.

```sql
CREATE TABLE telegram_interactions (
    id SERIAL PRIMARY KEY,
    telegram_user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    message_text TEXT,
    agent_type VARCHAR,
    response_text TEXT,
    session_id VARCHAR,
    timestamp TIMESTAMP DEFAULT now()
);
```

**Campos Detallados**:
- `id`: Identificador único de la interacción
- `telegram_user_id`: ID del usuario de Telegram (vincula con `usuarios.telegram_user_id`)
- `chat_id`: ID del chat de Telegram (puede ser diferente del user_id en grupos)
- `message_text`: Mensaje enviado por el usuario
- `agent_type`: Qué agente procesó la consulta ('ventas', 'cliente', 'administrativo')
- `response_text`: Respuesta generada por el agente
- `session_id`: Sesión diaria única (formato: 'telegram_CHATID_YYYYMMDD')
- `timestamp`: Momento exacto de la interacción

**Relaciones**:
- **Con `usuarios`**: FK implícita via `telegram_user_id`

**Índices para Performance**:
```sql
CREATE INDEX idx_telegram_interactions_user_id ON telegram_interactions(telegram_user_id);
CREATE INDEX idx_telegram_interactions_session ON telegram_interactions(session_id);
```

---

## 3. Tabla: `clients`
**Propósito**: Clientes del negocio (datos comerciales y contacto).

```sql
CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE,
    phone VARCHAR,
    address TEXT
);
```

**Campos Detallados**:
- `client_id`: Identificador único comercial
- `name`: Razón social o nombre del cliente
- `email`: Email principal de contacto (único en el sistema)
- `phone`: Teléfono principal de contacto
- `address`: Dirección física completa (para instalaciones)

**Relaciones**:
- **→ `installed_equipment`**: Un cliente puede tener múltiples equipos
- **→ `interventions`**: Un cliente puede tener múltiples servicios técnicos
- **→ `contracts`**: Un cliente puede tener múltiples contratos
- **→ `orders`**: Un cliente puede realizar múltiples pedidos
- **→ `chat_sessions`**: Un cliente puede tener múltiples conversaciones
- **Migración → `usuarios`**: Datos se copian a tabla usuarios para integración Telegram

**Casos de Uso**:
- Gestión comercial tradicional
- Facturación y contratos
- Direcciones de instalación

---

## 4. Tabla: `products`
**Propósito**: Catálogo completo de productos comercializados.

```sql
CREATE TABLE products (
    sku VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    price NUMERIC(10,2),
    spec_json JSONB
);
```

**Campos Detallados**:
- `sku`: Código único del producto (Stock Keeping Unit) - Clave primaria
- `name`: Nombre comercial del producto
- `description`: Descripción detallada para ventas
- `price`: Precio de venta al público (incluye 2 decimales)
- `spec_json`: Especificaciones técnicas en formato JSON flexible
  ```json
  {
    "dimensions": {"width": 30, "height": 40, "depth": 15},
    "weight": 2.5,
    "power": "220V",
    "features": ["wifi", "bluetooth", "sensor"],
    "warranty": "24 months"
  }
  ```

**Relaciones**:
- **→ `installed_equipment`**: Un producto puede estar instalado múltiples veces
- **→ `order_items`**: Un producto puede aparecer en múltiples pedidos
- **→ `stock`**: Un producto puede tener stock en múltiples almacenes

**Casos de Uso**:
- Cotizaciones y ventas
- Configuración de equipos instalados
- Control de inventario

---

## 5. Tabla: `technicians`
**Propósito**: Personal técnico para instalaciones y mantenimientos.

```sql
CREATE TABLE technicians (
    technician_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE,
    phone VARCHAR,
    zone VARCHAR
);
```

**Campos Detallados**:
- `technician_id`: Identificador único del técnico
- `name`: Nombre completo del técnico
- `email`: Email corporativo único
- `phone`: Teléfono de contacto directo
- `zone`: Zona geográfica asignada (para optimizar rutas)

**Relaciones**:
- **→ `interventions`**: Un técnico puede realizar múltiples intervenciones

**Casos de Uso**:
- Asignación de trabajos por zona
- Seguimiento de performance individual
- Contacto directo para urgencias

---

## 6. Tabla: `installed_equipment`
**Propósito**: Registro de equipos específicos instalados en ubicaciones de clientes.

```sql
CREATE TABLE installed_equipment (
    equipment_id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(client_id),
    sku VARCHAR REFERENCES products(sku),
    install_date DATE,
    status VARCHAR DEFAULT 'activo',
    config_json JSONB
);
```

**Campos Detallados**:
- `equipment_id`: Identificador único del equipo instalado (diferente del SKU)
- `client_id`: Cliente propietario del equipo
- `sku`: Tipo de producto instalado
- `install_date`: Fecha de instalación (importante para garantías)
- `status`: Estado actual ('activo', 'mantenimiento', 'averiado', 'retirado')
- `config_json`: Configuración específica de esta instalación
  ```json
  {
    "location": "Oficina principal, planta 2",
    "serial_number": "AIN-2024-001",
    "custom_settings": {"mode": "eco", "schedule": "9-18"},
    "network": {"ip": "192.168.1.100", "mac": "AA:BB:CC:DD:EE:FF"}
  }
  ```

**Relaciones**:
- **← `clients`**: Cada equipo pertenece a un cliente específico
- **← `products`**: Cada equipo es una instancia de un producto
- **→ `interventions`**: Un equipo puede tener múltiples intervenciones

**Lógica de Negocio**:
```
Producto (catálogo) → Venta → Instalación → Equipo instalado (con configuración específica)
```

---

## 7. Tabla: `interventions`
**Propósito**: Historial completo de servicios técnicos realizados.

```sql
CREATE TABLE interventions (
    intervention_id SERIAL PRIMARY KEY,
    technician_id INT REFERENCES technicians(technician_id),
    client_id INT REFERENCES clients(client_id),
    equipment_id INT REFERENCES installed_equipment(equipment_id),
    date DATE NOT NULL,
    type VARCHAR CHECK (type IN ('instalacion', 'mantenimiento', 'reparacion', 'retirada')),
    result TEXT,
    document_url TEXT
);
```

**Campos Detallados**:
- `intervention_id`: Identificador único de la intervención
- `technician_id`: Técnico responsable de la intervención
- `client_id`: Cliente que recibe el servicio
- `equipment_id`: Equipo específico intervenido
- `date`: Fecha de realización del servicio
- `type`: Tipo de intervención:
  - **'instalacion'**: Primera instalación del equipo
  - **'mantenimiento'**: Servicio preventivo programado
  - **'reparacion'**: Solución de averías o problemas
  - **'retirada'**: Desinstalación del equipo
- `result`: Descripción detallada del trabajo realizado y resultados
- `document_url`: Enlace a documentos (fotos, informes PDF, facturas)

**Relaciones**:
- **← `technicians`**: Cada intervención la realiza un técnico específico
- **← `clients`**: Cada intervención es para un cliente específico
- **← `installed_equipment`**: Cada intervención afecta a un equipo específico

**Casos de Uso**:
- Trazabilidad completa de servicios
- Programación de mantenimientos
- Facturación de servicios técnicos
- Análisis de performance de técnicos y equipos

---

## 8. Tabla: `contracts`
**Propósito**: Gestión de contratos y acuerdos comerciales.

```sql
CREATE TABLE contracts (
    contract_id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(client_id),
    start_date DATE,
    end_date DATE,
    type VARCHAR,
    terms TEXT
);
```

**Campos Detallados**:
- `contract_id`: Identificador único del contrato
- `client_id`: Cliente contratante
- `start_date`: Fecha de inicio de vigencia
- `end_date`: Fecha de finalización del contrato
- `type`: Tipo de contrato ('mantenimiento', 'alquiler', 'servicio_integral', 'garantia_extendida')
- `terms`: Términos y condiciones específicas del contrato

**Relaciones**:
- **← `clients`**: Cada contrato pertenece a un cliente específico

**Casos de Uso**:
- Contratos de mantenimiento programado
- Alquiler de equipos a largo plazo
- Garantías extendidas
- Acuerdos de servicio integral

---

## 9. Tabla: `orders`
**Propósito**: Pedidos realizados por clientes.

```sql
CREATE TABLE orders (
    order_id VARCHAR PRIMARY KEY,
    client_id INT REFERENCES clients(client_id),
    chat_id VARCHAR,
    total_amount NUMERIC(10,2),
    status VARCHAR DEFAULT 'pendiente'
);
```

**Campos Detallados**:
- `order_id`: Identificador alfanumérico único del pedido (ej: "ORD-2024-001")
- `client_id`: Cliente que realiza el pedido
- `chat_id`: Vinculación con sesión de chat donde se originó el pedido
- `total_amount`: Monto total del pedido (suma de todos los items)
- `status`: Estado del pedido ('pendiente', 'confirmado', 'en_proceso', 'enviado', 'entregado', 'cancelado')

**Relaciones**:
- **← `clients`**: Cada pedido pertenece a un cliente específico
- **← `chat_sessions`**: Un pedido puede originarse en una conversación
- **→ `order_items`**: Un pedido contiene múltiples productos

**Casos de Uso**:
- Pedidos desde el agente de ventas
- Pedidos desde conversaciones de chat
- Seguimiento de estado de pedidos

---

## 10. Tabla: `order_items`
**Propósito**: Detalle de productos específicos en cada pedido.

```sql
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id VARCHAR REFERENCES orders(order_id),
    product_sku VARCHAR REFERENCES products(sku),
    quantity INT,
    price NUMERIC(10,2)
);
```

**Campos Detallados**:
- `item_id`: Identificador único del item dentro del pedido
- `order_id`: Pedido al que pertenece este item
- `product_sku`: Producto específico solicitado
- `quantity`: Cantidad solicitada del producto
- `price`: Precio unitario del producto en este pedido (puede diferir del precio catálogo por descuentos)

**Relaciones**:
- **← `orders`**: Cada item pertenece a un pedido específico
- **← `products`**: Cada item referencia un producto del catálogo

**Casos de Uso**:
- Detalle de cotizaciones
- Facturación detallada
- Control de stock requerido

---

## 11. Tabla: `warehouses`
**Propósito**: Gestión de almacenes y ubicaciones de stock.

```sql
CREATE TABLE warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    name VARCHAR
);
```

**Campos Detallados**:
- `warehouse_id`: Identificador único del almacén
- `name`: Nombre descriptivo del almacén ("Almacén Central", "Depósito Norte")

**Relaciones**:
- **→ `stock`**: Un almacén puede contener múltiples productos

**Casos de Uso**:
- Gestión de inventario distribuido
- Optimización de logística por zonas

---

## 12. Tabla: `stock`
**Propósito**: Control de inventario por producto y almacén.

```sql
CREATE TABLE stock (
    stock_id SERIAL PRIMARY KEY,
    sku VARCHAR REFERENCES products(sku),
    warehouse_id INT REFERENCES warehouses(warehouse_id),
    quantity INT
);
```

**Campos Detallados**:
- `stock_id`: Identificador único del registro de stock
- `sku`: Producto en inventario
- `warehouse_id`: Almacén donde se encuentra el stock
- `quantity`: Cantidad disponible actual

**Relaciones**:
- **← `products`**: Cada registro de stock es para un producto específico
- **← `warehouses`**: Cada registro de stock está en un almacén específico

**Lógica de Negocio**:
- Permite stock distribuido: mismo producto en múltiples almacenes
- Control de disponibilidad para pedidos
- Optimización de envíos por proximidad

---

## 13. Tabla: `knowledge_feedback`
**Propósito**: Sistema de mejora continua para los agentes IA.

```sql
CREATE TABLE knowledge_feedback (
    feedback_id SERIAL PRIMARY KEY,
    question TEXT,
    expected_answer TEXT,
    user_type VARCHAR,
    status VARCHAR DEFAULT 'pendiente',
    created_at TIMESTAMP DEFAULT now()
);
```

**Campos Detallados**:
- `feedback_id`: Identificador único del feedback
- `question`: Pregunta que no fue respondida correctamente
- `expected_answer`: Respuesta correcta proporcionada por el usuario
- `user_type`: Tipo de usuario que proporcionó el feedback ('cliente', 'administrador', 'tecnico')
- `status`: Estado del procesamiento ('pendiente', 'revisado', 'implementado', 'descartado')
- `created_at`: Timestamp de creación del feedback

**Casos de Uso**:
- Entrenamiento y mejora de agentes IA
- Identificación de gaps de conocimiento
- Construcción de base de conocimiento

---

## 14. Tabla: `chat_sessions`
**Propósito**: Gestión de sesiones de conversación organizadas.

```sql
CREATE TABLE chat_sessions (
    chat_id VARCHAR PRIMARY KEY,
    order_id VARCHAR REFERENCES orders(order_id),
    client_id INT REFERENCES clients(client_id),
    start_timestamp TIMESTAMP DEFAULT now(),
    end_timestamp TIMESTAMP,
    topic VARCHAR
);
```

**Campos Detallados**:
- `chat_id`: Identificador único de la sesión (formato: "CHAT-YYYYMMDD-XXX")
- `order_id`: Pedido relacionado con la conversación (opcional)
- `client_id`: Cliente participante en la conversación
- `start_timestamp`: Inicio de la sesión de chat
- `end_timestamp`: Finalización de la sesión (NULL si está activa)
- `topic`: Tema principal de la conversación ('soporte', 'ventas', 'tecnico', 'consulta')

**Relaciones**:
- **← `orders`**: Una sesión puede estar relacionada con un pedido específico
- **← `clients`**: Cada sesión pertenece a un cliente específico
- **→ `chat_messages`**: Una sesión contiene múltiples mensajes

---

## 15. Tabla: `chat_messages`
**Propósito**: Almacenamiento de mensajes individuales en conversaciones.

```sql
CREATE TABLE chat_messages (
    message_id SERIAL PRIMARY KEY,
    chat_id VARCHAR REFERENCES chat_sessions(chat_id),
    message_timestamp TIMESTAMP NOT NULL,
    sender VARCHAR,
    message_text TEXT
);
```

**Campos Detallados**:
- `message_id`: Identificador único del mensaje
- `chat_id`: Sesión de chat a la que pertenece el mensaje
- `message_timestamp`: Momento exacto del mensaje
- `sender`: Identificación del remitente ('cliente', 'agente_ventas', 'agente_administrativo', 'agente_cliente', 'sistema')
- `message_text`: Contenido completo del mensaje

**Relaciones**:
- **← `chat_sessions`**: Cada mensaje pertenece a una sesión específica

**Casos de Uso**:
- Historial completo de conversaciones
- Análisis de calidad de servicio
- Auditoria de comunicaciones

---

# TABLAS DEL SISTEMA N8N (~35 tablas)

n8n crea automáticamente estas tablas para su funcionamiento. **NO las modifiques manualmente.**

## **Principales tablas de n8n:**

### **Gestión de Workflows**
- `workflow_entity` - Almacena los workflows importados
- `workflow_statistics` - Estadísticas de uso
- `execution_entity` - Historial de ejecuciones
- `execution_data` - Datos de cada ejecución

### **Credenciales y Seguridad**
- `credentials_entity` - Credenciales encriptadas (Telegram, PostgreSQL)
- `shared_credentials` - Permisos de credenciales
- `user` - Usuarios de n8n
- `role` - Roles y permisos

### **Configuración y Logs**
- `settings` - Configuración global de n8n
- `webhook_entity` - Webhooks registrados
- `tag_entity` - Tags para organización
- `variables` - Variables globales
- Y muchas más...

**Estas tablas son esenciales para que n8n funcione correctamente.**

---

# RELACIONES PRINCIPALES DEL SISTEMA

## **Flujo Telegram → Agentes:**
```
Usuario Telegram → tabla usuarios (por telegram_user_id) → Determinar rol → Dirigir al agente correcto
```

## **Flujo Comercial Completo:**
```
Cliente → Pedido → Productos → Instalación → Equipo instalado → Intervenciones → Contratos
```

## **Flujo de Comunicación:**
```
Chat Session → Chat Messages (historial completo)
Telegram Interactions (logs específicos de Telegram)
```

## **Flujo de Inventario:**
```
Productos → Stock por almacén → Pedidos → Instalaciones
```

---

# CONSULTAS IMPORTANTES

## **Verificar usuario de Telegram:**
```sql
SELECT u.nombre, u.rol, u.telegram_user_id 
FROM usuarios u 
WHERE u.telegram_user_id = 12345678;
```

## **Historial de interacciones Telegram:**
```sql
SELECT ti.message_text, ti.agent_type, ti.response_text, ti.timestamp
FROM telegram_interactions ti 
WHERE ti.telegram_user_id = 12345678 
ORDER BY ti.timestamp DESC;
```

## **Equipos de un cliente con último mantenimiento:**
```sql
SELECT ie.equipment_id, p.name, ie.status, 
       MAX(i.date) as ultimo_mantenimiento
FROM installed_equipment ie
JOIN products p ON ie.sku = p.sku
LEFT JOIN interventions i ON ie.equipment_id = i.equipment_id
WHERE ie.client_id = 1
GROUP BY ie.equipment_id, p.name, ie.status;
```

## **Stock disponible por almacén:**
```sql
SELECT p.name, w.name as almacen, s.quantity
FROM stock s
JOIN products p ON s.sku = p.sku
JOIN warehouses w ON s.warehouse_id = w.warehouse_id
WHERE s.quantity > 0
ORDER BY p.name, w.name;
```

---

# MANTENIMIENTO Y ESCALABILIDAD

## **Características Técnicas:**
- **JSONB**: Flexibilidad para especificaciones y configuraciones
- **Constraints**: Validaciones como CHECK en tipos de intervención
- **Índices**: Optimización para consultas frecuentes de Telegram
- **Foreign Keys**: Integridad referencial completa
- **Timestamps**: Control temporal preciso

## **Escalabilidad:**
- Nuevos productos → Especificaciones en JSONB
- Nuevos tipos de intervención → Modificar CHECK constraint
- Nuevos almacenes → Sin modificar estructura
- Múltiples agentes IA → Extensible via usuarios.rol
- Histórico completo → Sin pérdida de información 