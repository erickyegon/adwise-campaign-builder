"""
Streaming Service for AdWise AI Digital Marketing Campaign Builder

This module implements real-time streaming capabilities for AI content generation
using LangChain callbacks and WebSocket integration. It provides:
- Real-time streaming of AI-generated content
- Progress tracking for long-running workflows
- WebSocket integration for live updates
- Callback handlers for LangChain chains
- Event-driven architecture for real-time collaboration

Features:
- Streaming text generation with token-by-token updates
- Progress tracking for multi-step workflows
- WebSocket broadcasting for real-time collaboration
- Custom callback handlers for LangChain integration
- Error handling and connection management
- Rate limiting and performance optimization
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator, Callable
from datetime import datetime
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect
from langchain.callbacks import AsyncCallbackHandler
from langchain.schema import BaseMessage, LLMResult

from app.core.config import get_settings
from app.models.mongodb_models import User

logger = logging.getLogger(__name__)
settings = get_settings()


class StreamingCallbackHandler(AsyncCallbackHandler):
    """
    Custom callback handler for streaming LangChain responses
    
    Captures tokens, chain steps, and tool calls for real-time streaming
    """
    
    def __init__(self, session_id: str, websocket: Optional[WebSocket] = None):
        super().__init__()
        self.session_id = session_id
        self.websocket = websocket
        self.tokens = []
        self.current_step = ""
        self.start_time = datetime.utcnow()
        
    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Called when LLM starts generating"""
        await self._send_update({
            "type": "llm_start",
            "session_id": self.session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "prompts_count": len(prompts)
        })
        
    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when LLM generates a new token"""
        self.tokens.append(token)
        
        await self._send_update({
            "type": "token",
            "session_id": self.session_id,
            "token": token,
            "timestamp": datetime.utcnow().isoformat(),
            "total_tokens": len(self.tokens)
        })
        
    async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Called when LLM finishes generating"""
        full_text = "".join(self.tokens)
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        await self._send_update({
            "type": "llm_end",
            "session_id": self.session_id,
            "full_text": full_text,
            "timestamp": datetime.utcnow().isoformat(),
            "duration": duration,
            "token_count": len(self.tokens)
        })
        
    async def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Called when a chain starts"""
        chain_name = serialized.get("name", "Unknown Chain")
        self.current_step = chain_name
        
        await self._send_update({
            "type": "chain_start",
            "session_id": self.session_id,
            "chain_name": chain_name,
            "timestamp": datetime.utcnow().isoformat(),
            "inputs": inputs
        })
        
    async def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """Called when a chain ends"""
        await self._send_update({
            "type": "chain_end",
            "session_id": self.session_id,
            "chain_name": self.current_step,
            "timestamp": datetime.utcnow().isoformat(),
            "outputs": outputs
        })
        
    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Called when a tool starts"""
        tool_name = serialized.get("name", "Unknown Tool")
        
        await self._send_update({
            "type": "tool_start",
            "session_id": self.session_id,
            "tool_name": tool_name,
            "input": input_str,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    async def on_tool_end(self, output: str, **kwargs) -> None:
        """Called when a tool ends"""
        await self._send_update({
            "type": "tool_end",
            "session_id": self.session_id,
            "output": output,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    async def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Called when LLM encounters an error"""
        await self._send_update({
            "type": "error",
            "session_id": self.session_id,
            "error": str(error),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    async def _send_update(self, data: Dict[str, Any]) -> None:
        """Send update via WebSocket if available"""
        if self.websocket:
            try:
                await self.websocket.send_text(json.dumps(data))
            except Exception as e:
                logger.error(f"Failed to send WebSocket update: {e}")


class StreamingManager:
    """
    Manager for streaming AI content generation
    
    Handles WebSocket connections, session management, and real-time updates
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str) -> None:
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        logger.info(f"WebSocket connected for session {session_id}, user {user_id}")
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
    async def disconnect(self, session_id: str) -> None:
        """Disconnect a WebSocket client"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            
        logger.info(f"WebSocket disconnected for session {session_id}")
        
    async def send_to_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """Send data to a specific session"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_text(json.dumps(data))
                
                # Update last activity
                if session_id in self.active_sessions:
                    self.active_sessions[session_id]["last_activity"] = datetime.utcnow()
                    
            except WebSocketDisconnect:
                await self.disconnect(session_id)
            except Exception as e:
                logger.error(f"Failed to send to session {session_id}: {e}")
                
    async def broadcast_to_user(self, user_id: str, data: Dict[str, Any]) -> None:
        """Broadcast data to all sessions for a user"""
        user_sessions = [
            session_id for session_id, session_data in self.active_sessions.items()
            if session_data["user_id"] == user_id
        ]
        
        for session_id in user_sessions:
            await self.send_to_session(session_id, data)
            
    async def stream_content_generation(
        self,
        session_id: str,
        content_type: str,
        generation_function: Callable,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream content generation with progress updates"""
        try:
            # Send start notification
            start_data = {
                "type": "generation_start",
                "session_id": session_id,
                "content_type": content_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.send_to_session(session_id, start_data)
            yield start_data
            
            # Create callback handler for streaming
            callback_handler = StreamingCallbackHandler(
                session_id=session_id,
                websocket=self.active_connections.get(session_id)
            )
            
            # Execute generation function with callback
            result = await generation_function(callbacks=[callback_handler], **kwargs)
            
            # Send completion notification
            end_data = {
                "type": "generation_complete",
                "session_id": session_id,
                "content_type": content_type,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.send_to_session(session_id, end_data)
            yield end_data
            
        except Exception as e:
            error_data = {
                "type": "generation_error",
                "session_id": session_id,
                "content_type": content_type,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.send_to_session(session_id, error_data)
            yield error_data
            
    async def cleanup_inactive_sessions(self, timeout_minutes: int = 30) -> None:
        """Clean up inactive sessions"""
        cutoff_time = datetime.utcnow().timestamp() - (timeout_minutes * 60)
        
        inactive_sessions = [
            session_id for session_id, session_data in self.active_sessions.items()
            if session_data["last_activity"].timestamp() < cutoff_time
        ]
        
        for session_id in inactive_sessions:
            await self.disconnect(session_id)
            
        if inactive_sessions:
            logger.info(f"Cleaned up {len(inactive_sessions)} inactive sessions")


# Global streaming manager instance
_streaming_manager: Optional[StreamingManager] = None


async def get_streaming_manager() -> StreamingManager:
    """Get or create streaming manager instance"""
    global _streaming_manager
    
    if _streaming_manager is None:
        _streaming_manager = StreamingManager()
        
    return _streaming_manager


async def create_streaming_session(user_id: str) -> str:
    """Create a new streaming session"""
    session_id = str(uuid4())
    
    # Initialize session in manager
    manager = await get_streaming_manager()
    manager.active_sessions[session_id] = {
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "last_activity": datetime.utcnow()
    }
    
    logger.info(f"Created streaming session {session_id} for user {user_id}")
    
    return session_id
