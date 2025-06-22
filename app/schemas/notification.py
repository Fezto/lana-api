from sqlmodel import SQLModel
from typing import Optional, Literal
from datetime import datetime

class NotificationBase(SQLModel):
    user_id: int
    message: str
    method: Literal["email", "sms"]
    scheduled_at: datetime

class NotificationCreate(NotificationBase):
    pass

class NotificationRead(NotificationBase):
    id: int
    sent: bool

class NotificationUpdate(SQLModel):
    message: Optional[str] = None
    method: Optional[Literal["email", "sms"]] = None
    scheduled_at: Optional[datetime] = None
    sent: Optional[bool] = None
