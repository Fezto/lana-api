from sqlmodel import SQLModel
from typing import Optional, Literal
from datetime import date

class RecurringPaymentBase(SQLModel):
    user_id: int
    category_id: int
    amount: float
    description: Optional[str] = None
    frequency: Literal["daily", "weekly", "biweekly", "monthly"]
    next_due_date: date
    active: Optional[bool] = True

class RecurringPaymentCreate(SQLModel):  # No heredar de RecurringPaymentBase
    category_id: int
    amount: float
    description: Optional[str] = None
    frequency: Literal["daily", "weekly", "biweekly", "monthly"]
    next_due_date: date
    active: Optional[bool] = True

class RecurringPaymentRead(RecurringPaymentBase):
    id: int

class RecurringPaymentUpdate(SQLModel):
    category_id: Optional[int] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    frequency: Optional[Literal["daily", "weekly", "biweekly", "monthly"]] = None
    next_due_date: Optional[date] = None
    active: Optional[bool] = None