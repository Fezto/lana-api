from datetime import datetime
from sqlmodel import Field, Relationship

from .base import BaseModel



class PasswordReset(BaseModel, table=True):
    __tablename__ = "password_reset"
    user_id: int = Field(foreign_key="user.id")
    token: str
    expires_at: datetime
    used: bool = False

    user: "User" = Relationship(back_populates="password_reset_requests")