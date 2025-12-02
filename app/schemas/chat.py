"""
Chat and message schemas
"""
from datetime import datetime
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base message schema"""
    encrypted_payload: str
    message_hash: str = Field(..., min_length=66, max_length=66)  # 0x + 64 hex chars


class MessageCreate(MessageBase):
    """Schema for creating a message"""
    receiver_id: int


class MessageResponse(MessageBase):
    """Schema for message response"""
    id: int
    sender_id: int
    receiver_id: int
    blockchain_tx_hash: str | None = None
    timestamp: datetime

    class Config:
        from_attributes = True


class WebSocketMessage(BaseModel):
    """Schema for WebSocket message"""
    to_user_id: int
    payload: str
    message_hash: str = Field(..., min_length=66, max_length=66)


class ContactResponse(BaseModel):
    """Schema for contact response"""
    id: int
    username: str
    public_key: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class VerificationResponse(BaseModel):
    """Schema for blockchain verification response"""
    message_id: int
    message_hash: str
    verified: bool
    blockchain_tx_hash: str | None = None
