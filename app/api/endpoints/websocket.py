"""
WebSocket endpoint for real-time messaging
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.orm import Session
import logging
import json

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
        from jose import jwt, JWTError
        from app.core.config import settings

        # Decode token directly without raising HTTPException
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            logger.error("Token does not contain user_id")
            return None

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User not found for user_id: {user_id}")
            return None

        logger.info(f"Token verified successfully for user: {user.username} (id: {user_id})")
        return user

    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"WebSocket token verification failed: {e}")
        return None


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat
    Usage: ws://localhost:8000/ws?token=<jwt_token>
    """
    # Accept connection first (required by WebSocket protocol)
    await websocket.accept()

    logger.info("WebSocket connection accepted, extracting token...")

    # Extract token from query parameters manually
    token = None
    query_params = dict(websocket.query_params)
    token = query_params.get('token')

    if not token:
        logger.error("No token provided in query parameters")
        await websocket.send_json({
            "type": "error",
            "message": "Authentication token required"
        })
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Create database session manually
    from app.db.database import SessionLocal
    db = SessionLocal()
    user_id = None

    try:
        # Verify token
        user = verify_websocket_token(token, db)

        if not user:
            logger.warning("WebSocket connection rejected: Invalid token")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user_id = user.id
        logger.info(f"WebSocket connection authenticated for user {user_id}")

        # Register user connection in manager (without re-accepting)
        manager.active_connections[user_id] = websocket
        logger.info(f"User {user_id} registered. Total connections: {len(manager.active_connections)}")

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
                    
                    logger.info(f"Received message hash: {ws_message.message_hash}")

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
            if user_id:
                manager.disconnect(user_id)
                logger.info(f"User {user_id} disconnected")

        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {e}")
            if user_id:
                manager.disconnect(user_id)

    finally:
        # Always close the database session
        db.close()


@router.get("/test")
async def test_websocket_route():
    """
    Test endpoint to verify the WebSocket route is accessible
    """
    return {"status": "ok", "message": "WebSocket route is accessible"}


@router.get("/online")
async def get_online_users():
    """
    Get list of currently online users
    """
    return {
        "online_users": manager.get_online_users(),
        "count": len(manager.get_online_users())
    }
