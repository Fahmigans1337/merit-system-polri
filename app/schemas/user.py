from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.OPERATOR_SATKER
    satker_id: Optional[UUID] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password minimal 8 karakter')
        return v

    @field_validator('username')
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Username minimal 3 karakter')
        if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError('Username hanya boleh berisi huruf, angka, underscore, dash, dan titik')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    satker_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    @field_validator('password')
    @classmethod
    def password_min_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < 8:
            raise ValueError('Password minimal 8 karakter')
        return v


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: UserRole
    satker_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}
