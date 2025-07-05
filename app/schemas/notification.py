from sqlmodel import SQLModel
from typing import Optional, Literal
from datetime import datetime

class NotificationBase(SQLModel):
    user_id: int
    message: str
    method: Literal["email", "sms"]
    scheduled_at: datetime

class NotificationCreate(SQLModel):  # No heredar de NotificationBase
    message: str
    method: Literal["email", "sms"]
    scheduled_at: datetime

class NotificationRead(NotificationBase):
    id: int
    sent: bool

class NotificationUpdate(SQLModel):
    message: Optional[str] = None
    method: Optional[Literal["email", "sms"]] = None
    scheduled_at: Optional[datetime] = None
    sent: Optional[bool] = N