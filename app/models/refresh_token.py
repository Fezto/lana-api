from datetime import datetime, timezone
from sqlmodel import Field

from .base import BaseModel

class RefreshToken(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    token: str
    expires_at: datetime
    revoked: bool = False
