"""
Chat endpoints for conversation management.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging
import uuid

from database import get_db, User, Conversation, Message
from auth import get_current_user, verify_token
from agent import agent

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for sending a chat message."""
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat message."""
    response: str
    conversation_id: str
    message_id: str


class MessageResponse(BaseModel):
    """Response model for a single message."""
    id: str
    role: str
    content: str
    created_at: str


class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history."""
    conversation_id: str
    messages: List[MessageResponse]


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Send a message and get agent response."""
    try:
        # Extract token from Authorization header
        token = authorization.replace("Bearer ", "")
        
        # Verify token and get user
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get or create conversation
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user.id
            ).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conversation = Conversation(user_id=user.id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            logger.info(f"Created new conversation: {conversation.id}")
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()
        
        # Get message history
        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()
        
        message_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages[:-1]  # Exclude the just-added message
        ]
        
        # Process message with agent
        response_text = await agent.process_message(
            message=request.message,
            user_id=str(user.id),
            conversation_id=str(conversation.id),
            message_history=message_history
        )
        
        # Save assistant response
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text
        )
        db.add(assistant_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(assistant_message)
        
        logger.info(f"Message processed for conversation {conversation.id}")
        
        return ChatResponse(
            response=response_text,
            conversation_id=str(conversation.id),
            message_id=str(assistant_message.id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process message"
        )


@router.get("/history/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get conversation history."""
    try:
        # Extract token and verify user
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages
        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()
        
        message_responses = [
            MessageResponse(
                id=str(msg.id),
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at.isoformat()
            )
            for msg in messages
        ]
        
        return ConversationHistoryResponse(
            conversation_id=str(conversation.id),
            messages=message_responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversation history"
        )


@router.get("/conversations")
async def list_conversations(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """List all conversations for the current user."""
    try:
        # Extract token and verify user
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        # Get conversations
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).all()
        
        return {
            "conversations": [
                {
                    "id": str(conv.id),
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "message_count": len(conv.messages)
                }
                for conv in conversations
            ]
        }
        
    except Exception as e:
        logger.error(f"Error listing conversations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to list conversations"
        )


# ============= Gmail Endpoints =============

@router.get("/gmail/emails")
async def get_emails(
    authorization: str = Header(...),
    max_results: int = 10,
    query: str = "",
    db: Session = Depends(get_db)
):
    """Fetch emails from user's Gmail inbox."""
    from gmail_tools import gmail_tools
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        emails = await gmail_tools.fetch_emails(
            user_id=user_id,
            max_results=max_results,
            query=query
        )
        
        return {"emails": emails, "count": len(emails)}
        
    except Exception as e:
        logger.error(f"Error fetching emails: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch emails")


@router.get("/gmail/important")
async def get_important_emails(
    authorization: str = Header(...),
    days: int = 3,
    db: Session = Depends(get_db)
):
    """Get important/unread emails from the last N days."""
    from gmail_tools import gmail_tools
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        emails = await gmail_tools.get_important_emails(user_id=user_id, days=days)
        
        return {"emails": emails, "count": len(emails)}
        
    except Exception as e:
        logger.error(f"Error fetching important emails: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch important emails")


# ============= Calendar Endpoints =============

@router.get("/calendar/events")
async def get_calendar_events(
    authorization: str = Header(...),
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get upcoming calendar events."""
    from calendar_tools import calendar_tools
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        events = await calendar_tools.get_upcoming_events(user_id=user_id, days=days)
        
        return {"events": events, "count": len(events)}
        
    except Exception as e:
        logger.error(f"Error fetching calendar events: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch calendar events")


@router.get("/calendar/today")
async def get_today_schedule(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get today's schedule."""
    from calendar_tools import calendar_tools
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        events = await calendar_tools.get_today_schedule(user_id=user_id)
        
        return {"events": events, "count": len(events)}
        
    except Exception as e:
        logger.error(f"Error fetching today's schedule: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch today's schedule")


# ============= Memory Endpoints =============

@router.get("/memory")
async def get_user_memories(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get all learned memories for the current user."""
    from memory_brain import memory_brain
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        memories = await memory_brain.get_all_memories(user_id=user_id)
        
        return {"memories": memories, "count": len(memories)}
        
    except Exception as e:
        logger.error(f"Error fetching memories: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch memories")


@router.delete("/memory/{memory_id}")
async def delete_memory(
    memory_id: str,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Delete a specific memory entry."""
    from memory_brain import memory_brain
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        success = await memory_brain.delete_memory(user_id=user_id, memory_id=memory_id)
        
        if success:
            return {"success": True, "message": "Memory deleted"}
        else:
            raise HTTPException(status_code=404, detail="Memory not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting memory: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete memory")
