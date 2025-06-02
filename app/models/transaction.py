from enum import Enum
from datetime import datetime, date
from typing import Optional
from sqlmodel import Field, Column, Enum as SqlEnum, Relationship

from .base import BaseModel



class TransactionType(str, Enum):
    MANUAL = "manual"
    AUTO = "auto"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Transaction(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    category_id: int = Field(foreign_key="category.id", ondelete="CASCADE")
    amount: float
    date: date
    description: Optional[str] = None
    type: TransactionType = Field(default=TransactionType.MANUAL, sa_column=Column(SqlEnum(TransactionType)))
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, sa_column=Column(SqlEnum(TransactionStatus)))
    recurring_id: Optional[int] = Field(default=None, foreign_key="recurring_payment.id", ondelete="CASCADE")
    failure_reason: Optional[str] = None

    user: "User" = Relationship(back_populates="transactions")
    category: "Category" = Relationship(back_populates="transactions")
    recurring_payments: Optional["RecurringPayment"] = Relationship(back_populates="transactions")
