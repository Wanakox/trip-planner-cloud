import logging
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import quote

from app.core.config import settings
from app.core.exceptions import EmailDeliveryError
from app.core.security import create_email_verification_token
from app.models.user import User

logger = logging.getLogger(__name__)


def send_verification_email(user: User) -> None:
    token = create_email_verification_token(str(user.id), user.email)
    link = f"{settings.frontend_url.rstrip('/')}/verificar-correo?token={quote(token)}"
    message = EmailMessage()
    message["Subject"] = "Verifica tu correo en TripPlanner"
    message["From"] = settings.smtp_from_email
    message["To"] = user.email
    message.set_content(
        f"Hola {user.name},\n\nAbre este enlace para verificar tu correo:\n{link}\n\n"
        f"El enlace caduca en {settings.email_verification_expire_hours} horas.\n"
        "Si no has creado esta cuenta, puedes ignorar este mensaje.\n"
    )
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        logger.exception("No se pudo enviar el correo de verificación")
        raise EmailDeliveryError from exc
