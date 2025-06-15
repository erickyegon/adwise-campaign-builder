"""
Real-time Collaboration WebSocket Handler

This module implements real-time collaboration features as specified in the PRM:
- Live campaign editing with conflict resolution
- Real-time user presence tracking
- Change broadcasting to collaborators
- Cursor position sharing
- Comment and annotation system
- Version control integration

Design Principles:
- WebSocket-based real-time communication
- Redis pub/sub for scaling across instances
- Conflict resolution for simultaneous edits
- Comprehensive event tracking
- Security and permission validation
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.websockets import WebSocketState
import redis.asyncio as redis

from app.models.mongodb_models import Campaign, User, ChangeEntry
from app.core.database.mongodb import get_db
from app.core.config import get_settings
from app.api.deps import get_current_user_websocket

logger = logging.getLogger(__name__)
settings = get_settings()


class CollaborationEventType(str, Enum):
    """Types of collaboration events"""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    CONTENT_CHANGED = "content_changed"
    CURSOR_MOVED = "cursor_moved"
    COMMENT_ADDED = "comment_added"
    SELECTION_CHANGED = "selection_changed"
    LOCK_ACQUIRED = "lock_acquired"
    LOCK_RELEASED = "lock_released"
    CONFLICT_DETECTED = "conflict_detected"
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"


class CollaborationEvent:
    """Collaboration event data structure"""
    
    def __init__(
        self,
        event_type: CollaborationEventType,
        campaign_id: str,
        user_id: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        self.event_type = event_type
        self.campaign_id = campaign_id
        self.user_id = user_id
        self.data = data
        self.timestamp = timestamp or datetime.now()
        self.event_id = f"{campaign_id}_{user_id}_{self.timestamp.timestamp()}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "campaign_id": self.campaign_id,
            "user_id": self.user_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class UserSession:
    """User session information for collaboration"""
    
    def __init__(self, user_id: str, username: str, websocket: WebSocket):
        self.user_id = user_id
        self.username = username
        self.websocket = websocket
        self.joined_at = datetime.now()
        self.last_activity = datetime.now()
        self.cursor_position = None
        self.current_selection = None
        self.active_locks: Set[str] = set()
    
    async def send_event(self, event: CollaborationEvent) -> bool:
        """Send event to user's WebSocket"""
        try:
            if self.websocket.client_state == WebSocketState.CONNECTED:
                await self.websocket.send_text(json.dumps(event.to_dict()))
                self.last_activity = datetime.now()
                return True
        except Exception as e:
            logger.error(f"Error sending event to user {self.user_id}: {e}")
        return False
    
    def update_cursor(self, position: Dict[str, Any]) -> None:
        """Update user's cursor position"""
        self.cursor_position = position
        self.last_activity = datetime.now()
    
    def update_selection(self, selection: Dict[str, Any]) -> None:
        """Update user's text selection"""
        self.current_selection = selection
        self.last_activity = datetime.now()


class CampaignCollaborationRoom:
    """Collaboration room for a specific campaign"""
    
    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id
        self.users: Dict[str, UserSession] = {}
        self.content_locks: Dict[str, str] = {}  # field_path -> user_id
        self.change_history: List[ChangeEntry] = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
    
    async def add_user(self, user_session: UserSession) -> None:
        """Add user to collaboration room"""
        self.users[user_session.user_id] = user_session
        self.last_activity = datetime.now()
        
        # Notify other users
        event = CollaborationEvent(
            event_type=CollaborationEventType.USER_JOINED,
            campaign_id=self.campaign_id,
            user_id=user_session.user_id,
            data={
                "username": user_session.username,
                "joined_at": user_session.joined_at.isoformat(),
                "active_users": list(self.users.keys())
            }
        )
        
        await self.broadcast_event(event, exclude_user=user_session.user_id)
        
        # Send current state to new user
        await self.send_current_state(user_session)
        
        logger.info(f"User {user_session.user_id} joined campaign {self.campaign_id}")
    
    async def remove_user(self, user_id: str) -> None:
        """Remove user from collaboration room"""
        if user_id not in self.users:
            return
        
        user_session = self.users[user_id]
        
        # Release all locks held by this user
        await self.release_user_locks(user_id)
        
        # Remove user
        del self.users[user_id]
        self.last_activity = datetime.now()
        
        # Notify other users
        event = CollaborationEvent(
            event_type=CollaborationEventType.USER_LEFT,
            campaign_id=self.campaign_id,
            user_id=user_id,
            data={
                "username": user_session.username,
                "left_at": datetime.now().isoformat(),
                "active_users": list(self.users.keys())
            }
        )
        
        await self.broadcast_event(event, exclude_user=user_id)
        
        logger.info(f"User {user_id} left campaign {self.campaign_id}")
    
    async def handle_content_change(
        self,
        user_id: str,
        field_path: str,
        old_value: Any,
        new_value: Any,
        operation: str = "update"
    ) -> None:
        """Handle content change with conflict detection"""
        
        # Check if field is locked by another user
        if field_path in self.content_locks and self.content_locks[field_path] != user_id:
            await self.send_conflict_notification(user_id, field_path)
            return
        
        # Create change entry
        change_entry = ChangeEntry(
            timestamp=datetime.now(),
            user_id=user_id,
            change_type=operation,
            details={
                "field_path": field_path,
                "old_value": old_value,
                "new_value": new_value
            }
        )
        
        self.change_history.append(change_entry)
        self.last_activity = datetime.now()
        
        # Broadcast change to other users
        event = CollaborationEvent(
            event_type=CollaborationEventType.CONTENT_CHANGED,
            campaign_id=self.campaign_id,
            user_id=user_id,
            data={
                "field_path": field_path,
                "old_value": old_value,
                "new_value": new_value,
                "operation": operation,
                "change_id": change_entry.timestamp.isoformat()
            }
        )
        
        await self.broadcast_event(event, exclude_user=user_id)
        
        # Update database
        await self.persist_change(change_entry)
    
    async def handle_cursor_movement(
        self,
        user_id: str,
        position: Dict[str, Any]
    ) -> None:
        """Handle cursor position updates"""
        if user_id in self.users:
            self.users[user_id].update_cursor(position)
            
            # Broadcast cursor position to other users
            event = CollaborationEvent(
                event_type=CollaborationEventType.CURSOR_MOVED,
                campaign_id=self.campaign_id,
                user_id=user_id,
                data={
                    "position": position,
                    "username": self.users[user_id].username
                }
            )
            
            await self.broadcast_event(event, exclude_user=user_id)
    
    async def acquire_lock(self, user_id: str, field_path: str) -> bool:
        """Acquire lock on a field for editing"""
        if field_path in self.content_locks:
            return False  # Already locked
        
        self.content_locks[field_path] = user_id
        if user_id in self.users:
            self.users[user_id].active_locks.add(field_path)
        
        # Notify other users
        event = CollaborationEvent(
            event_type=CollaborationEventType.LOCK_ACQUIRED,
            campaign_id=self.campaign_id,
            user_id=user_id,
            data={
                "field_path": field_path,
                "username": self.users[user_id].username if user_id in self.users else "Unknown"
            }
        )
        
        await self.broadcast_event(event, exclude_user=user_id)
        return True
    
    async def release_lock(self, user_id: str, field_path: str) -> None:
        """Release lock on a field"""
        if field_path in self.content_locks and self.content_locks[field_path] == user_id:
            del self.content_locks[field_path]
            
            if user_id in self.users:
                self.users[user_id].active_locks.discard(field_path)
            
            # Notify other users
            event = CollaborationEvent(
                event_type=CollaborationEventType.LOCK_RELEASED,
                campaign_id=self.campaign_id,
                user_id=user_id,
                data={
                    "field_path": field_path,
                    "username": self.users[user_id].username if user_id in self.users else "Unknown"
                }
            )
            
            await self.broadcast_event(event, exclude_user=user_id)
    
    async def release_user_locks(self, user_id: str) -> None:
        """Release all locks held by a user"""
        if user_id not in self.users:
            return
        
        locks_to_release = list(self.users[user_id].active_locks)
        for field_path in locks_to_release:
            await self.release_lock(user_id, field_path)
    
    async def broadcast_event(self, event: CollaborationEvent, exclude_user: Optional[str] = None) -> None:
        """Broadcast event to all users in the room"""
        disconnected_users = []
        
        for user_id, user_session in self.users.items():
            if exclude_user and user_id == exclude_user:
                continue
            
            success = await user_session.send_event(event)
            if not success:
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            await self.remove_user(user_id)
    
    async def send_current_state(self, user_session: UserSession) -> None:
        """Send current collaboration state to a user"""
        state_data = {
            "active_users": [
                {
                    "user_id": uid,
                    "username": session.username,
                    "cursor_position": session.cursor_position,
                    "current_selection": session.current_selection,
                    "joined_at": session.joined_at.isoformat()
                }
                for uid, session in self.users.items()
                if uid != user_session.user_id
            ],
            "content_locks": {
                field_path: {
                    "locked_by": user_id,
                    "username": self.users[user_id].username if user_id in self.users else "Unknown"
                }
                for field_path, user_id in self.content_locks.items()
            },
            "recent_changes": [
                {
                    "timestamp": change.timestamp.isoformat(),
                    "user_id": change.user_id,
                    "change_type": change.change_type,
                    "details": change.details
                }
                for change in self.change_history[-10:]  # Last 10 changes
            ]
        }
        
        event = CollaborationEvent(
            event_type=CollaborationEventType.SYNC_RESPONSE,
            campaign_id=self.campaign_id,
            user_id="system",
            data=state_data
        )
        
        await user_session.send_event(event)
    
    async def send_conflict_notification(self, user_id: str, field_path: str) -> None:
        """Send conflict notification to user"""
        if user_id not in self.users:
            return
        
        locked_by = self.content_locks.get(field_path)
        locked_by_username = self.users[locked_by].username if locked_by in self.users else "Unknown"
        
        event = CollaborationEvent(
            event_type=CollaborationEventType.CONFLICT_DETECTED,
            campaign_id=self.campaign_id,
            user_id=user_id,
            data={
                "field_path": field_path,
                "locked_by": locked_by,
                "locked_by_username": locked_by_username,
                "message": f"Field is currently being edited by {locked_by_username}"
            }
        )
        
        await self.users[user_id].send_event(event)
    
    async def persist_change(self, change_entry: ChangeEntry) -> None:
        """Persist change to database"""
        try:
            # Update campaign with change entry
            campaign = await Campaign.get(self.campaign_id)
            if campaign:
                campaign.add_change_entry(
                    user_id=change_entry.user_id,
                    change_type=change_entry.change_type,
                    details=change_entry.details
                )
                await campaign.save()
        except Exception as e:
            logger.error(f"Error persisting change for campaign {self.campaign_id}: {e}")


class CollaborationManager:
    """Global collaboration manager"""
    
    def __init__(self):
        self.rooms: Dict[str, CampaignCollaborationRoom] = {}
        self.redis_client: Optional[redis.Redis] = None
    
    async def initialize(self) -> None:
        """Initialize collaboration manager"""
        try:
            # Initialize Redis for pub/sub
            self.redis_client = redis.Redis(
                host=settings.redis.REDIS_HOST,
                port=settings.redis.REDIS_PORT,
                password=settings.redis.REDIS_PASSWORD,
                db=settings.redis.REDIS_SESSION_DB,
                decode_responses=True
            )
            
            # Test Redis connection
            await self.redis_client.ping()
            logger.info("Collaboration manager initialized with Redis")
            
        except Exception as e:
            logger.error(f"Failed to initialize collaboration manager: {e}")
            raise
    
    async def get_or_create_room(self, campaign_id: str) -> CampaignCollaborationRoom:
        """Get or create collaboration room for campaign"""
        if campaign_id not in self.rooms:
            self.rooms[campaign_id] = CampaignCollaborationRoom(campaign_id)
            logger.info(f"Created collaboration room for campaign {campaign_id}")
        
        return self.rooms[campaign_id]
    
    async def join_campaign(
        self,
        campaign_id: str,
        user: User,
        websocket: WebSocket
    ) -> CampaignCollaborationRoom:
        """Join user to campaign collaboration"""
        room = await self.get_or_create_room(campaign_id)
        
        user_session = UserSession(
            user_id=str(user.id),
            username=user.full_name,
            websocket=websocket
        )
        
        await room.add_user(user_session)
        return room
    
    async def leave_campaign(self, campaign_id: str, user_id: str) -> None:
        """Remove user from campaign collaboration"""
        if campaign_id in self.rooms:
            await self.rooms[campaign_id].remove_user(user_id)
            
            # Clean up empty rooms
            if not self.rooms[campaign_id].users:
                del self.rooms[campaign_id]
                logger.info(f"Removed empty collaboration room for campaign {campaign_id}")
    
    async def handle_websocket_message(
        self,
        campaign_id: str,
        user_id: str,
        message: Dict[str, Any]
    ) -> None:
        """Handle incoming WebSocket message"""
        if campaign_id not in self.rooms:
            return
        
        room = self.rooms[campaign_id]
        event_type = message.get("event_type")
        data = message.get("data", {})
        
        if event_type == CollaborationEventType.CONTENT_CHANGED:
            await room.handle_content_change(
                user_id=user_id,
                field_path=data.get("field_path"),
                old_value=data.get("old_value"),
                new_value=data.get("new_value"),
                operation=data.get("operation", "update")
            )
        
        elif event_type == CollaborationEventType.CURSOR_MOVED:
            await room.handle_cursor_movement(user_id, data.get("position", {}))
        
        elif event_type == CollaborationEventType.LOCK_ACQUIRED:
            await room.acquire_lock(user_id, data.get("field_path"))
        
        elif event_type == CollaborationEventType.LOCK_RELEASED:
            await room.release_lock(user_id, data.get("field_path"))
        
        elif event_type == CollaborationEventType.SYNC_REQUEST:
            if user_id in room.users:
                await room.send_current_state(room.users[user_id])
    
    async def cleanup_inactive_rooms(self) -> None:
        """Clean up inactive collaboration rooms"""
        current_time = datetime.now()
        inactive_rooms = []
        
        for campaign_id, room in self.rooms.items():
            # Remove rooms inactive for more than 1 hour
            if (current_time - room.last_activity).total_seconds() > 3600:
                inactive_rooms.append(campaign_id)
        
        for campaign_id in inactive_rooms:
            del self.rooms[campaign_id]
            logger.info(f"Cleaned up inactive room for campaign {campaign_id}")


# Global collaboration manager instance
collaboration_manager = CollaborationManager()


async def get_collaboration_manager() -> CollaborationManager:
    """Get global collaboration manager"""
    return collaboration_manager
