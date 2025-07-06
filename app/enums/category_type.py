# app/enums.py (crear nuevo archivo)
from enum import Enum

class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"