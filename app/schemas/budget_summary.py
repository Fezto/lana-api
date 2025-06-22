# app/schemas/budget_summary.py
from sqlmodel import SQLModel
from typing import List, Literal

class BudgetSummaryItem(SQLModel):
    category_id: int
    category_name: str
    budgeted_amount: float
    spent_amount: float
    remaining: float
    percent_used: float

class BudgetSummaryResponse(SQLModel):
    month_year: str
    summary: List[BudgetSummaryItem]