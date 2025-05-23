from enum import Enum

from sqlmodel import Enum as SqlEnum
from sqlmodel import Field, Column

from .base import BaseModel

class CategoryType(str, Enum):
    income = "income"
    expense = "expense"

class Category(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    name: str
    type: CategoryType = Field(sa_column=Column(SqlEnum(CategoryType)))