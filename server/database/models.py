"""
Pydantic models for API requests/responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# Request Models
class ChatRequest(BaseModel):
    """Chat message request"""
    session_id: str = Field(description="Chat session ID")
    message: str = Field(description="User message")


class NewSessionRequest(BaseModel):
    """New session creation request"""
    session_id: Optional[str] = Field(None, description="Optional custom session ID")


# Response Models
class ChatResponse(BaseModel):
    """Chat message response"""
    session_id: str
    message: str
    role: str = "assistant"
    success: bool = True
    error: Optional[str] = None


class SessionResponse(BaseModel):
    """Session information"""
    id: str
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    """Message information"""
    id: int
    session_id: str
    role: str
    content: str
    created_at: str


class SessionHistoryResponse(BaseModel):
    """Full session with message history"""
    session: SessionResponse
    messages: List[MessageResponse]

