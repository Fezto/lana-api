from enum import Enum
from datetime import date
from typing import Optional, List
from sqlmodel import Field, Column, Enum as SqlEnum, Relationship

from .base import BaseModel
from ..enums.frequency import Frequency


class RecurringPayment(BaseModel, table=True):
    __tablename__ = "recurring_payment"
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    category_id: int = Field(foreign_key="category.id", ondelete="CASCADE")
    amount: float
    description: Optional[str] = None
    frequency: Frequency
    next_due_date: date
    active: bool = True

    user: "User" = Relationship(back_populates="recurring_payments")
    category: "Category" = Relationship(back_populates="recurring_payments")
    transactions: List["Transaction"] = Relationship(back_populates="recurring_payments")
