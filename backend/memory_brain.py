"""
Memory Brain system for the AI assistant.
Implements dynamic long-term memory that learns from conversations and emails.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import json
import re

from database import SessionLocal, MemoryEntry, User
from config import settings

logger = logging.getLogger(__name__)


# Memory categories
class MemoryCategory:
    PREFERENCE = "preference"      # User preferences ("I hate 9 AM meetings")
    PROJECT = "project"            # Project status updates
    CONTACT = "contact"            # Important people
    STYLE = "style"                # Communication style
    FACT = "fact"                  # General facts about user
    TASK = "task"                  # Tasks and todos
    SCHEDULE = "schedule"          # Scheduling preferences


# Memory source types
class MemorySource:
    CHAT = "chat"                  # Extracted from chat
    EMAIL = "email"                # Extracted from emails
    CALENDAR = "calendar"          # Extracted from calendar
    EXPLICIT = "explicit"          # User explicitly stated


class MemoryBrain:
    """
    Dynamic memory system that learns from user interactions.
    Stores and retrieves contextual information for personalized responses.
    """
    
    def __init__(self):
        """Initialize the Memory Brain."""
        self.preference_patterns = [
            (r"i (?:hate|don't like|dislike|avoid) (.+)", MemoryCategory.PREFERENCE),
            (r"i (?:love|like|prefer|enjoy) (.+)", MemoryCategory.PREFERENCE),
            (r"i never (.+)", MemoryCategory.PREFERENCE),
            (r"i always (.+)", MemoryCategory.PREFERENCE),
            (r"don't schedule (.+)", MemoryCategory.SCHEDULE),
            (r"(?:my name is|i'm|i am) (\w+)", MemoryCategory.FACT),
            (r"(?:call me|address me as) (\w+)", MemoryCategory.PREFERENCE),
        ]
        
        self.project_patterns = [
            (r"(?:project|task) (\w+) (?:is|was|has been) (delayed|cancelled|completed|on track)", MemoryCategory.PROJECT),
            (r"(\w+) project (?:is|was) (.*)", MemoryCategory.PROJECT),
            (r"deadline for (.+) (?:is|was|has been) (?:extended|moved|changed)", MemoryCategory.PROJECT),
        ]
    
    async def extract_facts_from_conversation(
        self, 
        messages: List[Dict[str, str]],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Extract facts and preferences from a conversation.
        
        Args:
            messages: List of conversation messages
            user_id: The user's ID
        
        Returns:
            List of extracted facts
        """
        extracted_facts = []
        
        for msg in messages:
            if msg.get('role') != 'user':
                continue
                
            content = msg.get('content', '').lower()
            
            # Check preference patterns
            for pattern, category in self.preference_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    fact = {
                        'content': msg.get('content', ''),
                        'category': category,
                        'source': MemorySource.CHAT,
                        'confidence': 0.9,
                        'extracted_value': match.group(1) if match.groups() else content
                    }
                    extracted_facts.append(fact)
            
            # Check project patterns
            for pattern, category in self.project_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    fact = {
                        'content': msg.get('content', ''),
                        'category': category,
                        'source': MemorySource.CHAT,
                        'confidence': 0.85,
                        'extracted_value': match.group(0)
                    }
                    extracted_facts.append(fact)
        
        # Store extracted facts
        if extracted_facts:
            await self.store_facts(user_id, extracted_facts)
        
        return extracted_facts
    
    async def extract_facts_from_email(
        self, 
        email: Dict[str, Any],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Extract facts from an email (project updates, contacts, etc.).
        
        Args:
            email: Email content dictionary
            user_id: The user's ID
        
        Returns:
            List of extracted facts
        """
        extracted_facts = []
        
        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()
        sender = email.get('from', '')
        
        # Extract project status updates
        status_keywords = ['delayed', 'completed', 'cancelled', 'on hold', 'urgent', 'deadline']
        for keyword in status_keywords:
            if keyword in subject or keyword in body:
                fact = {
                    'content': f"Email from {sender}: {email.get('subject', '')} - Status: {keyword}",
                    'category': MemoryCategory.PROJECT,
                    'source': MemorySource.EMAIL,
                    'confidence': 0.8,
                    'extra_data': {
                        'email_id': email.get('id'),
                        'sender': sender,
                        'keyword': keyword
                    }
                }
                extracted_facts.append(fact)
                break
        
        # Extract important contacts
        if 'urgent' in subject or 'important' in subject or 'asap' in body:
            fact = {
                'content': f"{sender} sent urgent/important email: {email.get('subject', '')}",
                'category': MemoryCategory.CONTACT,
                'source': MemorySource.EMAIL,
                'confidence': 0.75,
                'extra_data': {'sender': sender, 'email_id': email.get('id')}
            }
            extracted_facts.append(fact)
        
        # Store extracted facts
        if extracted_facts:
            await self.store_facts(user_id, extracted_facts)
        
        return extracted_facts
    
    async def store_facts(
        self, 
        user_id: str, 
        facts: List[Dict[str, Any]]
    ) -> int:
        """
        Store extracted facts in the database.
        
        Args:
            user_id: The user's ID
            facts: List of facts to store
        
        Returns:
            Number of facts stored
        """
        db = SessionLocal()
        stored_count = 0
        
        try:
            for fact in facts:
                # Check for duplicates
                existing = db.query(MemoryEntry).filter(
                    MemoryEntry.user_id == user_id,
                    MemoryEntry.content == fact['content']
                ).first()
                
                if existing:
                    # Update confidence if higher
                    if fact.get('confidence', 0) > existing.confidence:
                        existing.confidence = fact['confidence']
                        existing.updated_at = datetime.utcnow()
                    continue
                
                # Create new memory entry
                memory = MemoryEntry(
                    user_id=user_id,
                    content=fact['content'],
                    category=fact['category'],
                    source=fact['source'],
                    confidence=fact.get('confidence', 0.5),
                    extra_data=fact.get('extra_data', {})
                )
                db.add(memory)
                stored_count += 1
            
            db.commit()
            logger.info(f"Stored {stored_count} new memories for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error storing facts: {e}")
            db.rollback()
        finally:
            db.close()
        
        return stored_count
    
    async def retrieve_relevant_memories(
        self, 
        user_id: str, 
        context: str,
        categories: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories relevant to the current context.
        
        Args:
            user_id: The user's ID
            context: Current context/query
            categories: Optional filter by categories
            limit: Maximum memories to retrieve
        
        Returns:
            List of relevant memories
        """
        db = SessionLocal()
        try:
            query = db.query(MemoryEntry).filter(MemoryEntry.user_id == user_id)
            
            # Filter by categories if specified
            if categories:
                query = query.filter(MemoryEntry.category.in_(categories))
            
            # Get memories ordered by confidence and recency
            memories = query.order_by(
                MemoryEntry.confidence.desc(),
                MemoryEntry.updated_at.desc()
            ).limit(limit).all()
            
            # Score and filter by relevance to context
            context_lower = context.lower()
            relevant_memories = []
            
            for memory in memories:
                relevance_score = 0
                content_lower = memory.content.lower()
                
                # Check for keyword overlap
                context_words = set(context_lower.split())
                content_words = set(content_lower.split())
                overlap = len(context_words & content_words)
                relevance_score += overlap * 0.1
                
                # Category-based relevance
                if 'meeting' in context_lower or 'schedule' in context_lower:
                    if memory.category in [MemoryCategory.SCHEDULE, MemoryCategory.PREFERENCE]:
                        relevance_score += 0.3
                
                if 'email' in context_lower or 'mail' in context_lower:
                    if memory.category in [MemoryCategory.PROJECT, MemoryCategory.CONTACT]:
                        relevance_score += 0.3
                
                # Add all memories with some relevance or high confidence
                if relevance_score > 0 or memory.confidence > 0.7:
                    relevant_memories.append({
                        'id': str(memory.id),
                        'content': memory.content,
                        'category': memory.category,
                        'source': memory.source,
                        'confidence': memory.confidence,
                        'relevance': relevance_score,
                        'created_at': memory.created_at.isoformat()
                    })
            
            # Sort by combined score
            relevant_memories.sort(
                key=lambda x: x['confidence'] + x['relevance'], 
                reverse=True
            )
            
            return relevant_memories[:limit]
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []
        finally:
            db.close()
    
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all memories for a user.
        
        Args:
            user_id: The user's ID
        
        Returns:
            List of all memories
        """
        db = SessionLocal()
        try:
            memories = db.query(MemoryEntry).filter(
                MemoryEntry.user_id == user_id
            ).order_by(MemoryEntry.updated_at.desc()).all()
            
            return [{
                'id': str(m.id),
                'content': m.content,
                'category': m.category,
                'source': m.source,
                'confidence': m.confidence,
                'created_at': m.created_at.isoformat(),
                'updated_at': m.updated_at.isoformat()
            } for m in memories]
            
        except Exception as e:
            logger.error(f"Error getting all memories: {e}")
            return []
        finally:
            db.close()
    
    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """
        Delete a specific memory entry.
        
        Args:
            user_id: The user's ID
            memory_id: The memory entry ID
        
        Returns:
            True if deleted successfully
        """
        db = SessionLocal()
        try:
            memory = db.query(MemoryEntry).filter(
                MemoryEntry.id == memory_id,
                MemoryEntry.user_id == user_id
            ).first()
            
            if memory:
                db.delete(memory)
                db.commit()
                logger.info(f"Deleted memory {memory_id} for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    async def update_memory(
        self, 
        user_id: str, 
        memory_id: str, 
        new_content: Optional[str] = None,
        new_confidence: Optional[float] = None
    ) -> bool:
        """
        Update a memory entry.
        
        Args:
            user_id: The user's ID
            memory_id: The memory entry ID
            new_content: Optional new content
            new_confidence: Optional new confidence score
        
        Returns:
            True if updated successfully
        """
        db = SessionLocal()
        try:
            memory = db.query(MemoryEntry).filter(
                MemoryEntry.id == memory_id,
                MemoryEntry.user_id == user_id
            ).first()
            
            if memory:
                if new_content:
                    memory.content = new_content
                if new_confidence is not None:
                    memory.confidence = new_confidence
                memory.updated_at = datetime.utcnow()
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating memory: {e}")
            db.rollback()
            return False
        finally:
            db.close()


# Global instance
memory_brain = MemoryBrain()
