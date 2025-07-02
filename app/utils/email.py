# app/utils/email.py
import os
import httpx
from pydantic import EmailStr
from fastapi import HTTPException

# Configuración de Mailgun Sandbox
# Asegúrate de definir en tu .env:
#   MAILGUN_API_KEY=key-XXXXXXXXXXXXXXXXXXXXXXXX  <- tu API Key privado (no el Key ID)
#   MAILGUN_DOMAIN=sandboxaef9c7485f484502923079ad3d4b0e8f.mailgun.org
#   MAIL_FROM_ADDRESS=postmaster@sandboxaef9c7485f484502923079ad3d4b0e8f.mailgun.org
#   MAIL_FROM_NAME=Lana
#   API_URL=http://localhost:8000
#
# Importante:
# 1. Usa la API Key privada (que comienza con "key-"), no la Key ID como "7c5e3295-2b5a51cc".
# 2. En el modo sandbox, solo puedes enviar correos a direcciones que hayas verificado en el panel de Mailgun.

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAIL_FROM_ADDRESS = os.getenv("MAIL_FROM_ADDRESS")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "NoReply")
BASE_URL = os.getenv("API_URL", os.getenv("BASE_URL", "http://localhost:8000"))

# Validaciones
if not MAILGUN_API_KEY:
    raise RuntimeError("Debes definir MAILGUN_API_KEY (private key) en el .env")
if not MAILGUN_DOMAIN:
    raise RuntimeError("Debes definir MAILGUN_DOMAIN en el .env")
if not MAIL_FROM_ADDRESS:
    raise RuntimeError("Debes definir MAIL_FROM_ADDRESS en el .env")

FROM_HEADER = f"{MAIL_FROM_NAME} <{MAIL_FROM_ADDRESS}>"


async def send_verification_email(to: EmailStr, token: str) -> None:
    subject = "Verifica tu correo en Lana App"
    link = f"{BASE_URL}/auth/verify-email?token={token}"
    html = f"""
    <p>¡Bienvenido a Lana App!</p>
    <p>Por favor verifica tu correo haciendo clic en el siguiente enlace:</p>
    <p><a href=\"{link}\">{link}</a></p>
    <p>Si no solicitaste esto, ignora este mensaje.</p>
    """
    await _send_mailgun_email(to, subject, html)


async def send_reset_email(to: EmailStr, token: str) -> None:
    subject = "Restablece tu contraseña en Lana App"
    link = f"{BASE_URL}/auth/reset-password?token={token}"
    html = f"""
    <p>Hola,</p>
    <p>Has solicitado restablecer tu contraseña. Haz clic en el enlace a continuación:</p>
    <p><a href=\"{link}\">{link}</a></p>
    <p>Si no solicitaste esto, ignora este mensaje.</p>
    """
    await _send_mailgun_email(to, subject, html)


async def _send_mailgun_email(to: EmailStr, subject: str, html: str) -> None:
    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    data = {
        "from": FROM_HEADER,
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
    if response.status_code not in (200, 202):
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar email: {response.status_code} {response.text}"
        )
