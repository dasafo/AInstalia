--------- Tabla: clients ---------
CREATE TABLE IF NOT EXISTS clients (
client_id SERIAL PRIMARY KEY,
name VARCHAR NOT NULL,
email VARCHAR UNIQUE,
phone VARCHAR,
address TEXT
);

--------- Tabla: products ---------
CREATE TABLE IF NOT EXISTS products (
sku VARCHAR PRIMARY KEY,
name VARCHAR NOT NULL,
description TEXT,
price NUMERIC(10,2),
spec_json JSONB
);

--------- Tabla: technicians ---------
CREATE TABLE IF NOT EXISTS technicians (
technician_id SERIAL PRIMARY KEY,
name VARCHAR NOT NULL,
email VARCHAR UNIQUE,
phone VARCHAR,
zone VARCHAR
);

--------- Tabla: warehouses ---------
CREATE TABLE IF NOT EXISTS warehouses (
warehouse_id SERIAL PRIMARY KEY,
name VARCHAR
);

--------- Tabla: installed_equipment ---------
CREATE TABLE IF NOT EXISTS installed_equipment (
equipment_id SERIAL PRIMARY KEY,
client_id INT REFERENCES clients(client_id),
sku VARCHAR REFERENCES products(sku),
install_date DATE,
status VARCHAR DEFAULT 'activo',
config_json JSONB
);

--------- Tabla: interventions ---------
CREATE TABLE IF NOT EXISTS interventions (
intervention_id SERIAL PRIMARY KEY,
technician_id INT REFERENCES technicians(technician_id),
client_id INT REFERENCES clients(client_id),
equipment_id INT REFERENCES installed_equipment(equipment_id),
date DATE NOT NULL,
type VARCHAR CHECK (type IN ('instalacion', 'mantenimiento', 'reparacion', 'retirada')),
result TEXT,
document_url TEXT
);

--------- Tabla: contracts ---------
CREATE TABLE IF NOT EXISTS contracts (
contract_id SERIAL PRIMARY KEY,
client_id INT REFERENCES clients(client_id),
start_date DATE,
end_date DATE,
type VARCHAR,
terms TEXT
);

--------- Tabla: orders ---------
CREATE TABLE IF NOT EXISTS orders (
order_id VARCHAR PRIMARY KEY,
client_id INT REFERENCES clients(client_id),
chat_id VARCHAR,
total_amount NUMERIC(10,2),
status VARCHAR DEFAULT 'pendiente'
);

--------- Tabla: order_items ---------
CREATE TABLE IF NOT EXISTS order_items (
item_id SERIAL PRIMARY KEY,
order_id VARCHAR REFERENCES orders(order_id),
product_sku VARCHAR REFERENCES products(sku),
quantity INT,
price NUMERIC(10,2)
);

--------- Tabla: stock ---------
CREATE TABLE IF NOT EXISTS stock (
stock_id SERIAL PRIMARY KEY,
sku VARCHAR REFERENCES products(sku),
warehouse_id INT REFERENCES warehouses(warehouse_id),
quantity INT
);

--------- Tabla: knowledge_feedback ---------
CREATE TABLE IF NOT EXISTS knowledge_feedback (
feedback_id SERIAL PRIMARY KEY,
question TEXT,
expected_answer TEXT,
user_type VARCHAR,
status VARCHAR DEFAULT 'pendiente',
created_at TIMESTAMP DEFAULT now()
);

--------- Tabla: chat_sessions ---------
CREATE TABLE IF NOT EXISTS chat_sessions (
    chat_id VARCHAR PRIMARY KEY,
    order_id VARCHAR REFERENCES orders(order_id),
    client_id INT REFERENCES clients(client_id),
    start_timestamp TIMESTAMP DEFAULT now(),
    end_timestamp TIMESTAMP,
    topic VARCHAR
);

--------- Tabla: chat_messages ---------
CREATE TABLE IF NOT EXISTS chat_messages (
    message_id SERIAL PRIMARY KEY,
    chat_id VARCHAR REFERENCES chat_sessions(chat_id),
    message_timestamp TIMESTAMP NOT NULL,
    sender VARCHAR,
    message_text TEXT
);

-- ═══════════════════════════════════════════════════════════════
-- CARGA DE DATOS - Ejecutar después de crear todas las tablas
-- ═══════════════════════════════════════════════════════════════

\copy clients (name,email,phone,address) FROM '/data/clients.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy products FROM '/data/products.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy technicians (name,email,phone,zone) FROM '/data/technicians.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy warehouses (name) FROM '/data/warehouses.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy installed_equipment (client_id,sku,install_date,status,config_json) FROM '/data/installed_equipment.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy interventions (technician_id,client_id,equipment_id,date,type,result,document_url) FROM '/data/interventions.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy contracts (client_id,start_date,end_date,type,terms) FROM '/data/contracts.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy orders FROM '/data/orders.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8', NULL 'NULL');
\copy order_items (order_id,product_sku,quantity,price) FROM '/data/order_items.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy stock (sku,warehouse_id,quantity) FROM '/data/stock.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy knowledge_feedback (question,expected_answer,user_type,status) FROM '/data/knowledge_feedback.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy chat_sessions (chat_id,order_id,client_id,start_timestamp,end_timestamp,topic) FROM '/data/chat_sessions.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy chat_messages (chat_id,message_timestamp,sender,message_text) FROM '/data/chat_messages.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');