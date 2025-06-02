from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import Field, Relationship

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

    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
    password_reset_requests: List["PasswordReset"] = Relationship(back_populates="user")
    email_verification: "EmailVerification" = Relationship(back_populates="user")
    categories: List["Category"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")
    recurring_payments: List["RecurringPayment"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")

