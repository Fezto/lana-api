from enum import Enum
from datetime import datetime
from sqlmodel import Field, Column, Enum as SqlEnum, Relationship

from .base import BaseModel
from ..enums.notification_method import NotificationMethod


class Notification(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    message: str
    method: NotificationMethod
    scheduled_at: datetime
    sent: bool = False

    user: "User" = Relationship(back_populates="notifications")
