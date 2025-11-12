"""
User schemas for request/response validation
"""
from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)
    public_key: str | None = None  # Optional: public key for E2EE


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    public_key: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """Schema for user in database"""
    id: int
    hashed_password: str
    created_at: datetime

    class Config:
        from_attributes = True
