# app/schemas/category.py
from sqlmodel import SQLModel
from typing import Optional

from app.enums.category_type import CategoryType

class CategoryBase(SQLModel):
    name: str
    type: CategoryType  # Usar enum en lugar de Literal

class CategoryCreate(SQLModel):
    name: str
    type: CategoryType  # Enum aparece como select

class CategoryRead(CategoryBase):
    id: int
    user_id: int

class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    type: Optional[CategoryType] = None  # Enum opcional