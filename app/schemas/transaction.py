from sqlmodel import SQLModel
from typing import Optional, Literal
from datetime import date

from app.schemas.category import CategoryRead


class TransactionBase(SQLModel):
    user_id: int
    category_id: int
    amount: float
    date: date
    description: Optional[str] = None
    type: Literal["manual", "auto"] = "manual"
    status: Literal["pending", "completed", "failed"] = "pending"
    recurring_id: Optional[int] = None
    failure_reason: Optional[str] = None

class TransactionCreate(SQLModel):  # No heredar de TransactionBase
    category_id: int
    amount: float
    date: date
    description: Optional[str] = None
    type: Literal["manual", "auto"] = "manual"
    status: Literal["pending", "completed", "failed"] = "pending"
    recurring_id: Optional[int] = None
    failure_reason: Optional[str] = None


class TransactionRead(TransactionBase):
    id: int

class TransactionUpdate(SQLModel):
    category_id: Optional[int] = None
    amount: Optional[float] = None
    date: Optional[date] = None
    description: Optional[str] = None
    type: Optional[Literal["manual", "auto"]] = None
    status: Optional[Literal["pending", "completed", "failed"]] = None
    recurring_id: Optional[int] = None
    failure_reason: Optional[str] = None