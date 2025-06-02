from enum import Enum
from typing import List

from sqlmodel import Enum as SqlEnum, Relationship
from sqlmodel import Field, Column


from .base import BaseModel


class CategoryType(str, Enum):
    income = "income"
    expense = "expense"

class Category(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    name: str
    type: CategoryType = Field(sa_column=Column(SqlEnum(CategoryType)))

    user: "User" = Relationship(back_populates="categories")
    budgets: List["Budget"] = Relationship(back_populates="category")
    transactions: List["Transaction"] = Relationship(back_populates="category")
    recurring_payments: List["RecurringPayment"] = Relationship(back_populates="category")