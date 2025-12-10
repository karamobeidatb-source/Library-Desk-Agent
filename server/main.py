"""
FastAPI Backend Server for Library Desk Agent
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

from server.database.models import (
    ChatRequest, ChatResponse, NewSessionRequest,
    SessionResponse, MessageResponse, SessionHistoryResponse
)
from server.database.db import db
from server.agent.agent import run_agent

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Library Desk Agent API",
    description="AI Agent for library management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Library Desk Agent API",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat",
            "sessions": "/api/sessions",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the agent and get a response
    """
    try:
        session_id = request.session_id
        user_message = request.message
        
        # Ensure session exists
        sessions = db.get_sessions()
        session_exists = any(s["id"] == session_id for s in sessions)
        
        if not session_exists:
            db.create_session(session_id)
        
        # Save user message
        db.save_message(session_id, "user", user_message)
        
        # Get chat history (last 10 messages for context)
        messages = db.get_messages(session_id)
        chat_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages[-10:]  # Keep last 10 messages
        ]
        
        # Remove the just-added user message from history (agent will get it separately)
        chat_history = chat_history[:-1]
        
        # Run agent
        result = await run_agent(user_message, chat_history)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Agent error"))
        
        agent_response = result["output"]
        
        # Save assistant response
        db.save_message(session_id, "assistant", agent_response)
        
        # Update session timestamp
        db.update_session_timestamp(session_id)
        
        return ChatResponse(
            session_id=session_id,
            message=agent_response,
            role="assistant",
            success=True
        )
    
    except HTTPException:
        raise
    except Exception as e:
        return ChatResponse(
            session_id=request.session_id,
            message=f"An error occurred: {str(e)}",
            role="assistant",
            success=False,
            error=str(e)
        )


@app.post("/api/sessions/new", response_model=SessionResponse)
async def create_new_session(request: NewSessionRequest = None):
    """
    Create a new chat session (or reuse existing one)
    """
    try:
        session_id = request.session_id if request and request.session_id else str(uuid.uuid4())
        
        # Check if session already exists
        sessions = db.get_sessions()
        if any(s["id"] == session_id for s in sessions):
            # Session already exists, just return it
            existing = next(s for s in sessions if s["id"] == session_id)
            return SessionResponse(
                id=existing["id"],
                created_at=existing["created_at"],
                updated_at=existing["updated_at"]
            )
        
        # Create new session
        db.create_session(session_id)
        
        return SessionResponse(
            id=session_id,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Session list endpoints removed - using single default session
# The frontend no longer needs to list or switch between sessions


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session (not implemented in db.py yet, placeholder)
    """
    return {"message": "Session deletion not implemented yet"}


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", 8000))
    
    print(f"🚀 Starting Library Desk Agent API on http://{host}:{port}")
    print(f"📚 Database: {os.getenv('DATABASE_PATH', './db/library.db')}")
    print(f"🤖 LLM Model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    
    uvicorn.run(app, host=host, port=port)

