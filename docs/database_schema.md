# Documentación de la Base de Datos - AInstalia

## Descripción General

La base de datos de AInstalia está diseñada para gestionar un negocio de instalación y mantenimiento de equipos. El sistema maneja clientes, productos, técnicos, equipos instalados, intervenciones técnicas, contratos, pedidos y un sistema de chat integrado.

## Arquitectura y Lógica del Negocio

El sistema se basa en los siguientes flujos principales:

1. **Gestión de Clientes y Productos**: Los clientes pueden adquirir productos que luego se instalan como equipos
2. **Gestión Técnica**: Los técnicos realizan instalaciones, mantenimientos y reparaciones en equipos de clientes
3. **Gestión Comercial**: Se manejan contratos, pedidos y facturación
4. **Gestión de Inventario**: Control de stock en múltiples almacenes
5. **Comunicación**: Sistema de chat para soporte y ventas

## Tablas y Estructura

### 1. Tabla: `clients`
**Propósito**: Almacena información de los clientes del negocio.

```sql
CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE,
    phone VARCHAR,
    address TEXT
);
```

**Campos**:
- `client_id`: Identificador único automático
- `name`: Nombre del cliente (obligatorio)
- `email`: Email único del cliente
- `phone`: Teléfono de contacto
- `address`: Dirección completa

**Relaciones**: Es referenciada por `installed_equipment`, `interventions`, `contracts`, `orders` y `chat_sessions`.

### 2. Tabla: `products`
**Propósito**: Catálogo de productos disponibles para venta e instalación.

```sql
CREATE TABLE products (
    sku VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    price NUMERIC(10,2),
    spec_json JSONB
);
```

**Campos**:
- `sku`: Código único del producto (Stock Keeping Unit)
- `name`: Nombre del producto (obligatorio)
- `description`: Descripción detallada
- `price`: Precio del producto (hasta 2 decimales)
- `spec_json`: Especificaciones técnicas en formato JSON flexible

**Relaciones**: Es referenciada por `installed_equipment`, `order_items` y `stock`.

### 3. Tabla: `technicians`
**Propósito**: Información de los técnicos que realizan instalaciones y mantenimientos.

```sql
CREATE TABLE technicians (
    technician_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE,
    phone VARCHAR,
    zone VARCHAR
);
```

**Campos**:
- `technician_id`: Identificador único automático
- `name`: Nombre del técnico (obligatorio)
- `email`: Email único del técnico
- `phone`: Teléfono de contacto
- `zone`: Zona geográfica asignada al técnico

**Relaciones**: Es referenciada por `interventions`.

### 4. Tabla: `installed_equipment`
**Propósito**: Registro de equipos instalados en las ubicaciones de los clientes.

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

**Campos**:
- `equipment_id`: Identificador único del equipo instalado
- `client_id`: Referencia al cliente propietario
- `sku`: Referencia al producto base
- `install_date`: Fecha de instalación
- `status`: Estado del equipo (por defecto 'activo')
- `config_json`: Configuración específica del equipo instalado

**Lógica**: Un producto del catálogo se convierte en equipo instalado cuando se coloca en la ubicación de un cliente.

### 5. Tabla: `interventions`
**Propósito**: Registro de todas las intervenciones técnicas realizadas.

```sql
CREATE TABLE interventions (
    intervention_id SERIAL PRIMARY KEY,
    technician_id INT REFERENCES technicians(technician_id),
    client_id INT REFERENCES clients(client_id),
    equipment_id INT REFERENCES installed_equipment(equipment_id),
    date DATE NOT NULL,
    type VARCHAR CHECK (type IN ('instalacion', 'mantenimiento', 'reparacion')),
    result TEXT,
    document_url TEXT
);
```

**Campos**:
- `intervention_id`: Identificador único de la intervención
- `technician_id`: Técnico que realizó la intervención
- `client_id`: Cliente al que se le prestó el servicio
- `equipment_id`: Equipo sobre el que se intervino
- `date`: Fecha de la intervención (obligatorio)
- `type`: Tipo de intervención (instalación, mantenimiento o reparación)
- `result`: Descripción del resultado o trabajo realizado
- `document_url`: URL a documentos relacionados (informes, fotos, etc.)

**Lógica**: Registra la trazabilidad completa de servicios técnicos.

### 6. Tabla: `contracts`
**Propósito**: Gestión de contratos con clientes.

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

**Campos**:
- `contract_id`: Identificador único del contrato
- `client_id`: Cliente con quien se firma el contrato
- `start_date`: Fecha de inicio del contrato
- `end_date`: Fecha de finalización del contrato
- `type`: Tipo de contrato (mantenimiento, alquiler, etc.)
- `terms`: Términos y condiciones del contrato

### 7. Tabla: `orders`
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

**Campos**:
- `order_id`: Identificador único del pedido (alfanumérico)
- `client_id`: Cliente que realizó el pedido
- `chat_id`: Vinculación con sesión de chat donde se originó
- `total_amount`: Monto total del pedido
- `status`: Estado del pedido (por defecto 'pendiente')

### 8. Tabla: `order_items`
**Propósito**: Detalle de productos en cada pedido.

```sql
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id VARCHAR REFERENCES orders(order_id),
    product_sku VARCHAR REFERENCES products(sku),
    quantity INT,
    price NUMERIC(10,2)
);
```

**Campos**:
- `item_id`: Identificador único del item
- `order_id`: Pedido al que pertenece el item
- `product_sku`: Producto específico
- `quantity`: Cantidad solicitada
- `price`: Precio unitario del producto en este pedido

### 9. Tabla: `warehouses`
**Propósito**: Gestión de almacenes para control de inventario.

```sql
CREATE TABLE warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    name VARCHAR
);
```

**Campos**:
- `warehouse_id`: Identificador único del almacén
- `name`: Nombre del almacén

### 10. Tabla: `stock`
**Propósito**: Control de inventario por almacén y producto.

```sql
CREATE TABLE stock (
    stock_id SERIAL PRIMARY KEY,
    sku VARCHAR REFERENCES products(sku),
    warehouse_id INT REFERENCES warehouses(warehouse_id),
    quantity INT
);
```

**Campos**:
- `stock_id`: Identificador único del registro de stock
- `sku`: Producto en inventario
- `warehouse_id`: Almacén donde se encuentra
- `quantity`: Cantidad disponible

**Lógica**: Permite tener diferentes cantidades del mismo producto en múltiples almacenes.

### 11. Tabla: `knowledge_feedback`
**Propósito**: Sistema de retroalimentación para mejorar el conocimiento del sistema.

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

**Campos**:
- `feedback_id`: Identificador único del feedback
- `question`: Pregunta realizada por el usuario
- `expected_answer`: Respuesta esperada o correcta
- `user_type`: Tipo de usuario que proporcionó el feedback
- `status`: Estado del procesamiento del feedback
- `created_at`: Timestamp de creación

### 12. Tabla: `chat_sessions`
**Propósito**: Gestión de sesiones de conversación con clientes.

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

**Campos**:
- `chat_id`: Identificador único de la sesión de chat
- `order_id`: Pedido relacionado con la conversación (opcional)
- `client_id`: Cliente participante en la conversación
- `start_timestamp`: Inicio de la conversación
- `end_timestamp`: Fin de la conversación
- `topic`: Tema principal de la conversación

### 13. Tabla: `chat_messages`
**Propósito**: Almacenamiento de mensajes individuales dentro de las conversaciones.

```sql
CREATE TABLE chat_messages (
    message_id SERIAL PRIMARY KEY,
    chat_id VARCHAR REFERENCES chat_sessions(chat_id),
    message_timestamp TIMESTAMP NOT NULL,
    sender VARCHAR,
    message_text TEXT
);
```

**Campos**:
- `message_id`: Identificador único del mensaje
- `chat_id`: Sesión de chat a la que pertenece
- `message_timestamp`: Momento exacto del mensaje
- `sender`: Quién envió el mensaje ('cliente', 'agente', 'sistema')
- `message_text`: Contenido del mensaje

## Relaciones Principales

### Relaciones de Clientes
- Un cliente puede tener múltiples equipos instalados
- Un cliente puede tener múltiples intervenciones
- Un cliente puede tener múltiples contratos
- Un cliente puede realizar múltiples pedidos
- Un cliente puede tener múltiples sesiones de chat

### Relaciones de Productos
- Un producto puede estar instalado en múltiples ubicaciones (como equipos)
- Un producto puede estar en múltiples pedidos
- Un producto puede tener stock en múltiples almacenes

### Relaciones de Técnicos
- Un técnico puede realizar múltiples intervenciones
- Las intervenciones están asociadas a técnicos, clientes y equipos específicos

### Flujo de Negocio Típico

1. **Venta**: Cliente realiza pedido → Se crea order con order_items
2. **Instalación**: Producto se instala → Se crea installed_equipment → Se registra intervention tipo 'instalacion'
3. **Mantenimiento**: Técnico realiza servicio → Se registra intervention tipo 'mantenimiento'
4. **Soporte**: Cliente contacta → Se crea chat_session con chat_messages

## Características Técnicas

- **JSONB**: Se utiliza para almacenar especificaciones de productos y configuraciones de equipos de forma flexible
- **Constraints**: Se implementan validaciones como CHECK en el tipo de intervención
- **Referencias**: Integridad referencial mediante FOREIGN KEYS
- **Timestamps**: Control temporal en chat y feedback
- **Códigos alfanuméricos**: order_id y chat_id permiten códigos legibles por humanos

## Escalabilidad y Mantenimiento

El diseño permite:
- Agregar nuevos tipos de productos mediante JSONB
- Expandir tipos de intervenciones modificando el CHECK constraint
- Agregar nuevos almacenes sin modificar estructura
- Historico completo de comunicaciones cliente-empresa
- Trazabilidad completa de equipos desde venta hasta mantenimiento 