# Verificación de correo en Render

1. Configura y verifica el remitente en Brevo. Crea una clave SMTP y copia el usuario SMTP (puede diferir del correo de acceso).
2. En Render, añade al servicio backend: `SMTP_HOST=smtp-relay.brevo.com`, `SMTP_PORT=2525`, `SMTP_USERNAME`, `SMTP_PASSWORD` (clave SMTP), `SMTP_FROM_EMAIL` (remitente verificado) y `FRONTEND_URL=https://trip-planner-frontend-vnir.onrender.com`. Mantén la clave en variables privadas; nunca en Git.
3. En el SQL Editor de Supabase ejecuta **solo** `verify_email_migration.sql`. No uses `schema.sql` en la base existente: comienza eliminando todas las tablas.
4. Despliega backend y frontend. Registra una cuenta de prueba, abre el enlace del correo y comprueba que el inicio de sesión falla antes de verificar y funciona después. Prueba también el reenvío.

La migración marca como pendientes todas las cuentas actuales. Sus titulares deberán solicitar un enlace en `/verificar-correo` y abrirlo para iniciar sesión de nuevo. La actualización del correo de una cuenta verificada también requiere verificar el nuevo correo. Los enlaces caducan a las 24 horas y se limita el reenvío a uno por minuto por cuenta.

La eliminación de un viaje y la de una cuenta borran primero sus objetos del bucket `tripplanner-files` y después las filas de PostgreSQL. Si falla Storage, la eliminación de la base no continúa. Storage y PostgreSQL no comparten transacción: un fallo posterior de la base puede dejar registros de objetos ya eliminados y requerir una limpieza manual.
