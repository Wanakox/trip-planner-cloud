-- Ejecutar en el SQL Editor de Supabase ANTES de desplegar el nuevo backend.
-- Habilitar previamente pg_cron en Integrations > Cron si aún no está activo.
-- Las cuentas anteriores quedan con NULL y no serán eliminadas por este job.
ALTER TABLE public.usuario
    ADD COLUMN IF NOT EXISTS registro_caduca_en TIMESTAMPTZ;

-- Cada cinco minutos borra las cuentas nuevas sin verificar cuyo plazo
-- fijo de 24 horas desde el registro haya terminado.
SELECT cron.schedule(
    'tripplanner-expired-registrations',
    '*/5 * * * *',
    $$DELETE FROM public.usuario
      WHERE correo_verificado = FALSE
        AND registro_caduca_en <= now()$$
);
