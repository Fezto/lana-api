from enum import Enum
from datetime import date
from typing import Optional
from sqlmodel import Field, Column, Enum as SqlEnum

from .base import BaseModel

class Frequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"

class RecurringPayment(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    amount: float
    description: Optional[str] = None
    frequency: Frequency = Field(sa_column=Column(SqlEnum(Frequency)))
    next_due_date: date
    active: bool = True
