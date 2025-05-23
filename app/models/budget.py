from datetime import datetime, timezone
from sqlmodel import Field

from .base import BaseModel

class Budget(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    amount: float
    month_year: str  # formato 'YYYY-MM'
