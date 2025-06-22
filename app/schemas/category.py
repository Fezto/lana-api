from sqlmodel import SQLModel
from typing import Literal, Optional

class CategoryBase(SQLModel):
    user_id: int
    name: str
    type: Literal["income", "expense"]

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int

class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    type: Optional[Literal["income", "expense"]] = None
