"""
WebSocket endpoint for real-time messaging
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, status
from sqlalchemy.orm import Session
import logging
import json

from app.core.security import decode_access_token
from app.db.database import get_db
from app.db.models import Message, User
from app.services.websocket import manager
from app.schemas.chat import WebSocketMessage

router = APIRouter()
logger = logging.getLogger(__name__)


def verify_websocket_token(token: str, db: Session) -> User:
    """
    Verify JWT token for WebSocket connection
    """
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")

        if user_id is None:
            return None

        user = db.query(User).filter(User.id == user_id).first()
        return user

    except Exception as e:
        logger.error(f"WebSocket token verification failed: {e}")
        return None


@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat
    Usage: ws://localhost:8000/ws?token=<jwt_token>
    """
    # Verify token
    user = verify_websocket_token(token, db)

    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = user.id
    logger.info(f"WebSocket connection attempt from user {user_id}")

    # Connect user
    await manager.connect(user_id, websocket)

    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "message": f"Connected as {user.username}",
        "user_id": user_id
    })

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)

                # Validate message structure
                ws_message = WebSocketMessage(**message_data)

                # Get sender and receiver
                sender = user
                receiver_id = ws_message.to_user_id

                # Check if receiver exists
                receiver = db.query(User).filter(User.id == receiver_id).first()
                if not receiver:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Receiver not found"
                    })
                    continue

                # Save message to database
                new_message = Message(
                    sender_id=sender.id,
                    receiver_id=receiver_id,
                    encrypted_payload=ws_message.payload,
                    message_hash=ws_message.message_hash
                )

                db.add(new_message)
                db.commit()
                db.refresh(new_message)

                logger.info(f"Message saved: {new_message.id} from {sender.id} to {receiver_id}")

                # Trigger asynchronous blockchain notarization
                from app.services.notarization import notarize_message_async
                import asyncio
                asyncio.create_task(asyncio.to_thread(notarize_message_async, new_message.id, None))

                # Prepare message for delivery
                delivery_message = {
                    "type": "message",
                    "message_id": new_message.id,
                    "from_user_id": sender.id,
                    "from_username": sender.username,
                    "payload": ws_message.payload,
                    "message_hash": ws_message.message_hash,
                    "timestamp": new_message.timestamp.isoformat()
                }

                # Send to receiver if online
                if manager.is_user_online(receiver_id):
                    await manager.send_personal_message(delivery_message, receiver_id)
                    logger.info(f"Message delivered to online user {receiver_id}")
                else:
                    logger.info(f"Receiver {receiver_id} is offline, message saved")

                # Send confirmation to sender
                await websocket.send_json({
                    "type": "sent",
                    "message_id": new_message.id,
                    "to_user_id": receiver_id,
                    "timestamp": new_message.timestamp.isoformat()
                })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })

            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}"
                })

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        logger.info(f"User {user_id} disconnected")

    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)


@router.get("/online")
async def get_online_users():
    """
    Get list of currently online users
    """
    return {
        "online_users": manager.get_online_users(),
        "count": len(manager.get_online_users())
    }
