from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field
from .base import BaseModel


class User(BaseModel, table=True):
    first_name: str
    last_name: str
    email: str = Field(unique=True, index=True)
    telephone: Optional[str] = None
    password_hash: str
    email_verified: bool = False
    verification_token: Optional[str] = None
    verification_expires_at: Optional[datetime] = None
