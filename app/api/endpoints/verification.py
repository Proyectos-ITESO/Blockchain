"""
Message verification endpoint
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import User, Message
from app.schemas.chat import VerificationResponse
from app.services.blockchain import blockchain_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/verify/{message_id}", response_model=VerificationResponse)
async def verify_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify a message's integrity on the blockchain

    Checks if the message hash is registered on the blockchain
    """
    # Get message from database
    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    # Check if user has access to this message
    if message.sender_id != current_user.id and message.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Verify hash on blockchain
    try:
        is_verified = blockchain_service.verify_hash(message.message_hash)

        return VerificationResponse(
            message_id=message.id,
            message_hash=message.message_hash,
            verified=is_verified,
            blockchain_tx_hash=message.blockchain_tx_hash
        )

    except Exception as e:
        logger.error(f"Error verifying message {message_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying message on blockchain"
        )


@router.post("/notarize/{message_id}")
async def notarize_message(
    message_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger notarization of a message
    (Useful for testing or re-trying failed notarizations)
    """
    # Get message from database
    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    # Check if user is the sender
    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the sender can notarize a message"
        )

    # Check if already notarized
    if message.blockchain_tx_hash:
        return {
            "message": "Message already notarized",
            "tx_hash": message.blockchain_tx_hash
        }

    # Add background task to notarize
    from app.services.notarization import notarize_message_async

    background_tasks.add_task(notarize_message_async, message.id, db)

    return {
        "message": "Notarization started",
        "message_id": message.id
    }


@router.get("/hash-info/{message_id}")
async def get_hash_info(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed blockchain information about a message hash
    """
    # Get message from database
    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    # Check if user has access to this message
    if message.sender_id != current_user.id and message.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Get hash info from blockchain
    try:
        hash_info = blockchain_service.get_hash_info(message.message_hash)

        if hash_info is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Blockchain service unavailable"
            )

        registered, timestamp, registrar = hash_info

        return {
            "message_id": message.id,
            "message_hash": message.message_hash,
            "registered": registered,
            "timestamp": timestamp,
            "registrar": registrar,
            "blockchain_tx_hash": message.blockchain_tx_hash
        }

    except Exception as e:
        logger.error(f"Error getting hash info for message {message_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving hash info from blockchain"
        )
