from sqlmodel import SQLModel
from typing import Literal, Optional

class CategoryBase(SQLModel):
    user_id: int
    name: str
    type: Literal["income", "expense"]

class CategoryCreate(SQLModel):  # No heredar de CategoryBase
    name: str
    type: Literal["income", "expense"]

class CategoryRead(CategoryBase):
    id: int

class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    type: Optional[Literal["income", "expense"]] = None