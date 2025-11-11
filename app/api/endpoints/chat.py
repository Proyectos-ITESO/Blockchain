"""
Chat API endpoints: contacts, message history
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import User, Contact, Message
from app.schemas.chat import MessageResponse, ContactResponse

router = APIRouter()


@router.get("/contacts", response_model=List[ContactResponse])
async def get_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of user's contacts
    Returns users with whom the current user has exchanged messages
    """
    # Find all users who have exchanged messages with current user
    contacts_query = db.query(User).join(
        Message,
        or_(
            and_(Message.sender_id == User.id, Message.receiver_id == current_user.id),
            and_(Message.receiver_id == User.id, Message.sender_id == current_user.id)
        )
    ).filter(User.id != current_user.id).distinct()

    contacts = contacts_query.all()

    return contacts


@router.post("/contacts/{user_id}", status_code=status.HTTP_201_CREATED)
async def add_contact(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a user to contacts
    """
    # Check if user exists
    contact_user = db.query(User).filter(User.id == user_id).first()
    if not contact_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if already in contacts
    existing_contact = db.query(Contact).filter(
        Contact.user_id == current_user.id,
        Contact.contact_id == user_id
    ).first()

    if existing_contact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already in contacts"
        )

    # Add contact
    new_contact = Contact(
        user_id=current_user.id,
        contact_id=user_id
    )

    db.add(new_contact)
    db.commit()

    return {"message": "Contact added successfully"}


@router.get("/chat/{user_id}", response_model=List[MessageResponse])
async def get_chat_history(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat history with a specific user
    Returns encrypted message payloads in chronological order
    """
    # Check if user exists
    other_user = db.query(User).filter(User.id == user_id).first()
    if not other_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get messages between current user and specified user
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.timestamp.desc()).limit(limit).offset(offset).all()

    # Reverse to get chronological order (oldest first)
    messages.reverse()

    return messages


@router.get("/messages/recent", response_model=List[MessageResponse])
async def get_recent_messages(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent messages for current user (both sent and received)
    """
    messages = db.query(Message).filter(
        or_(
            Message.sender_id == current_user.id,
            Message.receiver_id == current_user.id
        )
    ).order_by(Message.timestamp.desc()).limit(limit).all()

    return messages


@router.get("/users/search")
async def search_users(
    query: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search for users by username
    """
    if len(query) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be at least 2 characters"
        )

    users = db.query(User).filter(
        User.username.ilike(f"%{query}%"),
        User.id != current_user.id
    ).limit(limit).all()

    return [{"id": user.id, "username": user.username} for user in users]
