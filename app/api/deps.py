"""
Dependency injection for API endpoints
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import oauth2_scheme, decode_access_token
from app.db.database import get_db
from app.db.models import User


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    payload = decode_access_token(token)
    username: str = payload.get("sub")
    user_id: int = payload.get("user_id")

    if username is None or user_id is None:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user
