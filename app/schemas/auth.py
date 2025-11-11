"""
Authentication schemas
"""
from pydantic import BaseModel


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data"""
    username: str | None = None
    user_id: int | None = None


class LoginRequest(BaseModel):
    """Login credentials"""
    username: str
    password: str
