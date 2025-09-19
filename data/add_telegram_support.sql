-- ══════════════════════════════════════════════════════════════════
-- SCRIPT: Añadir soporte para Telegram Bot
-- Ejecutar DESPUÉS de create_tables.sql
-- ══════════════════════════════════════════════════════════════════

-- Crear tabla usuarios (requerida por los workflows de agentes)
CREATE TABLE IF NOT EXISTS usuarios (
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

-- Migrar datos existentes de clients a usuarios
INSERT INTO usuarios (nombre, email, telefono, rol, activo)
SELECT 
    name,
    email,
    phone,
    'cliente',
    true
FROM clients
WHERE email IS NOT NULL
ON CONFLICT (email) DO NOTHING;

-- Crear algunos usuarios administradores de ejemplo
INSERT INTO usuarios (nombre, email, rol, activo) VALUES
    ('Admin AInstalia', 'admin@ainstalia.com', 'administrador', true),
    ('Soporte Técnico', 'soporte@ainstalia.com', 'tecnico', true)
ON CONFLICT (email) DO NOTHING;

-- Crear índices para optimizar consultas de Telegram
CREATE INDEX IF NOT EXISTS idx_usuarios_telegram_user_id ON usuarios(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON usuarios(rol);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);

-- Crear tabla para logs de interacciones con el bot
CREATE TABLE IF NOT EXISTS telegram_interactions (
    id SERIAL PRIMARY KEY,
    telegram_user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    message_text TEXT,
    agent_type VARCHAR,
    response_text TEXT,
    session_id VARCHAR,
    timestamp TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_telegram_interactions_user_id ON telegram_interactions(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_interactions_session ON telegram_interactions(session_id);

-- Ver estadísticas después de la migración
SELECT 
    'USUARIOS MIGRADOS' as tabla,
    COUNT(*) as total,
    COUNT(CASE WHEN rol = 'cliente' THEN 1 END) as clientes,
    COUNT(CASE WHEN rol = 'administrador' THEN 1 END) as administradores,
    COUNT(CASE WHEN rol = 'tecnico' THEN 1 END) as tecnicos
FROM usuarios; 