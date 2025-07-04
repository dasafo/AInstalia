-- Script de inicialización para la base de datos de Chatwoot
-- Se ejecuta después de crear las tablas de AInstalia

-- Crear la base de datos de Chatwoot si no existe
SELECT 'CREATE DATABASE chatwoot_production'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'chatwoot_production')\gexec

-- Otorgar permisos al usuario postgres en la base de datos de Chatwoot
GRANT ALL PRIVILEGES ON DATABASE chatwoot_production TO postgres;

-- Conectar a la base de datos de Chatwoot y crear extensiones necesarias
\c chatwoot_production;

-- Crear extensión para UUIDs si no existe
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear extensión para funciones criptográficas si no existe
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Comentario informativo
COMMENT ON DATABASE chatwoot_production IS 'Base de datos para Chatwoot - Sistema de soporte al cliente';