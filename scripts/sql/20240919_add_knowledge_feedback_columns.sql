-- Manual migration: agrega columnas para feedback de conocimiento
-- Ejecutar contra la base de datos PostgreSQL de AInstalia antes de desplegar.

ALTER TABLE IF EXISTS knowledge_feedback
    ADD COLUMN IF NOT EXISTS user_comment TEXT,
    ADD COLUMN IF NOT EXISTS rating SMALLINT CHECK (rating BETWEEN 1 AND 5),
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();
