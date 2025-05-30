# app/utils/email.py
import os
import httpx
from pydantic import EmailStr
from fastapi import HTTPException

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAIL_FROM = os.getenv("MAIL_FROM", f"noreply@{MAILGUN_DOMAIN}")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
    raise RuntimeError("Debes definir MAILGUN_API_KEY y MAILGUN_DOMAIN en el .env")


async def send_verification_email(to: EmailStr, token: str) -> None:
    subject = "Verifica tu correo en Lana App"
    link = f"{BASE_URL}/auth/verify-email?token={token}"
    html = f"""
    <p>¡Bienvenido a Lana App!</p>
    <p>Por favor verifica tu correo haciendo clic en el siguiente enlace:</p>
    <p><a href="{link}">{link}</a></p>
    <p>Si no solicitaste esto, ignora este mensaje.</p>
    """
    await _send_mailgun_email(to, subject, html)


async def send_reset_email(to: EmailStr, token: str) -> None:
    subject = "Restablece tu contraseña en Lana App"
    link = f"{BASE_URL}/auth/reset-password?token={token}"
    html = f"""
    <p>Hola,</p>
    <p>Has solicitado restablecer tu contraseña. Haz clic en el enlace a continuación:</p>
    <p><a href="{link}">{link}</a></p>
    <p>Si no solicitaste esto, ignora este mensaje.</p>
    """
    await _send_mailgun_email(to, subject, html)


async def _send_mailgun_email(to: EmailStr, subject: str, html: str) -> None:
    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    data = {
        "from": MAIL_FROM,
        "to": to,
        "subject": subject,
        "html": html,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            auth=("api", MAILGUN_API_KEY),
            data=data,
            timeout=10.0,
        )
    if response.status_code != 200:
        # En producción podrías loguear más info o enviar a Sentry
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar email: {response.status_code} {response.text}"
        )
