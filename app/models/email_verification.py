from datetime import datetime
from sqlmodel import Field, Relationship

from .base import BaseModel


class EmailVerification(BaseModel, table=True):
    __tablename__ = "email_verifications"
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    token: str
    expires_at: datetime
    used: bool = False

    user: "User" = Relationship(back_populates="email_verification")