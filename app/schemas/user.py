# app/schemas/user.py
from typing import Optional
from datetime import datetime
from pydantic import EmailStr
from sqlmodel import SQLModel

class UserBase(SQLModel):
    first_name: str
    last_name: str
    email: EmailStr
    telephone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    email_verified: bool
    created_on: datetime
    modified_on: Optional[datetime]

class UserUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    telephone: Optional[str] = None
    password: Optional[str] = None
