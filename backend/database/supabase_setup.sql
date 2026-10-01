-- TripPlanner - Supabase-specific setup
-- Requires pg_cron to be enabled in Supabase.

SELECT cron.schedule(
    'tripplanner-expired-registrations',
    '*/5 * * * *',
    $$DELETE FROM public.usuario
      WHERE correo_verificado = FALSE
        AND registro_caduca_en <= now()$$
);