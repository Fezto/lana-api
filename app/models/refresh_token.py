from datetime import datetime, timezone
from sqlmodel import Field, Relationship

from .base import BaseModel



class RefreshToken(BaseModel, table=True):
    __tablename__ = "refresh_taken"
    user_id: int = Field(foreign_key="user.id")
    token: str
    expires_at: datetime
    revoked: bool = False

    user: "User" = Relationship(back_populates="refresh_tokens")