"""
WebSocket connection manager for real-time chat
"""
from typing import Dict, List
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for users
    Maps user_id -> WebSocket connection
    """

    def __init__(self):
        # Active connections: user_id -> WebSocket
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        """
        Accept and register a new WebSocket connection
        """
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, user_id: int):
        """
        Remove a WebSocket connection
        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, user_id: int):
        """
        Send a message to a specific user
        """
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_json(message)
                logger.debug(f"Message sent to user {user_id}")
                return True
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                self.disconnect(user_id)
                return False
        else:
            logger.warning(f"User {user_id} not connected")
            return False

    async def broadcast(self, message: dict, exclude_user: int = None):
        """
        Broadcast a message to all connected users (except excluded)
        """
        disconnected = []

        for user_id, websocket in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue

            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                disconnected.append(user_id)

        # Clean up disconnected users
        for user_id in disconnected:
            self.disconnect(user_id)

    def is_user_online(self, user_id: int) -> bool:
        """
        Check if a user is currently connected
        """
        return user_id in self.active_connections

    def get_online_users(self) -> List[int]:
        """
        Get list of all online user IDs
        """
        return list(self.active_connections.keys())


# Global connection manager instance
manager = ConnectionManager()
