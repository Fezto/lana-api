from sqlmodel import SQLModel
from typing import Optional
from decimal import Decimal


class BudgetBase(SQLModel):
    user_id: int
    category_id: int
    amount: Decimal
    month_year: str  # formato 'YYYY-MM'!!!


class BudgetCreate(SQLModel):  # No heredar de BudgetBase
    category_id: int
    amount: Decimal
    month_year: str


class BudgetRead(BudgetBase):
    id: int


class BudgetUpdate(SQLModel):
    amount: Optional[Decimal] = None