"""
Schemas Pydantic para User
Arquivo: backend/app/schemas/user.py
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    crea: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    plan: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str = ""
    refresh_token: str = ""
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None

