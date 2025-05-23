from datetime import datetime
from sqlmodel import Field

from .base import BaseModel

class PasswordResetRequest(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    token: str
    expires_at: datetime
    used: bool = False