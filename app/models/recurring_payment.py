from enum import Enum
from datetime import date
from typing import Optional, List
from sqlmodel import Field, Column, Enum as SqlEnum, Relationship

from .base import BaseModel



class Frequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"

class RecurringPayment(BaseModel, table=True):
    __tablename__ = "recurring_payment"
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    amount: float
    description: Optional[str] = None
    frequency: Frequency = Field(sa_column=Column(SqlEnum(Frequency)))
    next_due_date: date
    active: bool = True

    user: "User" = Relationship(back_populates="recurring_payments")
    category: "Category" = Relationship(back_populates="recurring_payments")
    transactions: List["Transaction"] = Relationship(back_populates="recurring")
