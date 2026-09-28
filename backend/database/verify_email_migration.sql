-- Ejecutar una sola vez en la base existente de Supabase.
-- Los usuarios actuales necesitarán verificar su correo para iniciar sesión.
-- No ejecutar schema.sql sobre la base existente: ese archivo elimina las tablas.
ALTER TABLE usuario
    ADD COLUMN IF NOT EXISTS correo_verificado BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS verificacion_enviada_en TIMESTAMPTZ;
