from pydantic import EmailStr
from sqlmodel import SQLModel
from typing import Literal

class LoginData(SQLModel):
    email: EmailStr
    password: str

class LogoutRequest(SQLModel):
    refresh_token: str


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"

class RefreshTokenRequest(SQLModel):
    refresh_token: str

class ForgotPasswordRequest(SQLModel):
    email: EmailStr

class ResetPasswordRequest(SQLModel):
    token: str
    password: str