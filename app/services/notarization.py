"""
Asynchronous notarization service
Handles background tasks for registering message hashes on blockchain
"""
import logging
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Message
from app.services.blockchain import blockchain_service

logger = logging.getLogger(__name__)


def notarize_message_async(message_id: int, db: Session = None):
    """
    Asynchronously notarize a message on the blockchain

    This function is called as a background task after a message is sent
    It registers the message hash on the blockchain and updates the database

    Args:
        message_id: ID of the message to notarize
        db: Optional database session (will create new if not provided)
    """
    # Create new database session if not provided
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # Get message from database
        message = db.query(Message).filter(Message.id == message_id).first()

        if not message:
            logger.error(f"Message {message_id} not found for notarization")
            return

        # Skip if already notarized
        if message.blockchain_tx_hash:
            logger.info(f"Message {message_id} already notarized: {message.blockchain_tx_hash}")
            return

        logger.info(f"Starting notarization for message {message_id}")

        # Register hash on blockchain
        tx_hash = blockchain_service.register_hash(message.message_hash)

        if tx_hash:
            # Update message with transaction hash
            message.blockchain_tx_hash = tx_hash
            db.commit()

            logger.info(f"Message {message_id} notarized successfully. Tx: {tx_hash}")
            return tx_hash

            # Optional: Wait for transaction confirmation
            # This might take a while, so we do it asynchronously
            # receipt = blockchain_service.wait_for_transaction(tx_hash, timeout=120)
            # if receipt:
            #     logger.info(f"Transaction {tx_hash} confirmed in block {receipt['blockNumber']}")

        else:
            logger.error(f"Failed to notarize message {message_id}")
            return None

    except Exception as e:
        logger.error(f"Error notarizing message {message_id}: {e}")
        db.rollback()

    finally:
        if close_db:
            db.close()


def batch_notarize_messages(message_ids: list, db: Session = None):
    """
    Notarize multiple messages in batch

    Args:
        message_ids: List of message IDs to notarize
        db: Optional database session
    """
    logger.info(f"Starting batch notarization for {len(message_ids)} messages")

    for message_id in message_ids:
        try:
            notarize_message_async(message_id, db)
        except Exception as e:
            logger.error(f"Error in batch notarization for message {message_id}: {e}")
            continue

    logger.info("Batch notarization completed")


def retry_failed_notarizations(db: Session = None):
    """
    Retry notarization for messages that don't have a blockchain transaction hash

    This can be run periodically to ensure all messages are notarized
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # Find messages without blockchain_tx_hash
        messages = db.query(Message).filter(Message.blockchain_tx_hash.is_(None)).limit(100).all()

        if not messages:
            logger.info("No failed notarizations to retry")
            return

        logger.info(f"Retrying notarization for {len(messages)} messages")

        for message in messages:
            try:
                notarize_message_async(message.id, db)
            except Exception as e:
                logger.error(f"Error retrying notarization for message {message.id}: {e}")
                continue

        logger.info("Retry completed")

    finally:
        if close_db:
            db.close()
