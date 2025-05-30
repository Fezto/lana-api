from enum import Enum
from datetime import datetime
from sqlmodel import Field, Column, Enum as SqlEnum, Relationship

from .base import BaseModel


class NotificationMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"

class Notification(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    message: str
    method: NotificationMethod = Field(sa_column=Column(SqlEnum(NotificationMethod)))
    scheduled_at: datetime
    sent: bool = False

    user: "User" = Relationship(back_populates="notifications")
