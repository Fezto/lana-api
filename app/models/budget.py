from typing import Optional

from sqlmodel import Field, Relationship

from .base import BaseModel



class Budget(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    amount: float
    month_year: str  # formato 'YYYY-MM'

    user: "User" = Relationship(back_populates="budgets")
    category: "Category" = Relationship(back_populates="budgets")
