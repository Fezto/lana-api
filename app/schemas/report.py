from sqlmodel import SQLModel
from typing import List, Literal
from datetime import date

# Income vs Expense per period
class IncomeExpenseItem(SQLModel):
    period: str       # e.g. '2025-06'
    income: float
    expense: float

class IncomeExpenseResponse(SQLModel):
    items: List[IncomeExpenseItem]

# Totals by category for a date range

class CategoryReportItem(SQLModel):
    category_id: int
    category_name: str
    total: float

class CategoryReportResponse(SQLModel):
    start_date: date
    end_date: date
    items: List[CategoryReportItem]

# Time series trends
gran: Literal["daily", "weekly", "monthly"]
class TrendItem(SQLModel):
    period: str      # date string according to granularity
    total: float

class TrendReportResponse(SQLModel):
    granularity: Literal["daily", "weekly", "monthly"]
    items: List[TrendItem]