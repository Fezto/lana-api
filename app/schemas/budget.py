from sqlmodel import SQLModel
from typing import Optional
from decimal import Decimal

class BudgetBase(SQLModel):
    user_id: int
    category_id: int
    amount: Decimal
    month_year: str  # formato 'YYYY-MM'

class BudgetCreate(SQLModel):  # ✅ Correcto: sin user_id
    category_id: int
    amount: Decimal
    month_year: str

class BudgetRead(BudgetBase):
    id: int

class BudgetUpdate(SQLModel):
    category_id: Optional[int] = None  # ✅ Agregar
    amount: Optional[Decimal] = None
    month_year: Optional[str] = None   # ✅ Agregar