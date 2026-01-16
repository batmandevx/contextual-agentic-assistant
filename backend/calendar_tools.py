"""
Google Calendar integration tools for the AI assistant.
Provides functionality to view, create, and manage calendar events.
"""
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from database import SessionLocal, User, Session as DBSession
from auth import decrypt_token

logger = logging.getLogger(__name__)


class CalendarTools:
    """Google Calendar API tools for the agent."""
    
    def __init__(self):
        """Initialize Calendar tools."""
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
    
    def _get_calendar_service(self, user_id: str, db: Session):
        """Get authenticated Calendar service for a user."""
        try:
            # Get user session with stored tokens
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            session = db.query(DBSession).filter(
                DBSession.user_id == user_id
            ).order_by(DBSession.created_at.desc()).first()
            
            if not session:
                raise ValueError(f"No active session for user {user_id}")
            
            # Decrypt access token
            access_token = decrypt_token(session.access_token_encrypted)
            refresh_token = decrypt_token(session.refresh_token_encrypted)
            
            # Create credentials
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                scopes=self.scopes
            )
            
            # Build Calendar service
            service = build('calendar', 'v3', credentials=credentials)
            return service
            
        except Exception as e:
            logger.error(f"Error getting Calendar service: {e}")
            raise
    
    async def get_upcoming_events(
        self, 
        user_id: str, 
        days: int = 7,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming calendar events for the next N days.
        
        Args:
            user_id: The user's ID
            days: Number of days to look ahead
            max_results: Maximum number of events
        
        Returns:
            List of upcoming events
        """
        db = SessionLocal()
        try:
            service = self._get_calendar_service(user_id, db)
            
            # Calculate time range
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days)).isoformat() + 'Z'
            
            # Get events
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event.get('summary', '(No title)'),
                    'start': start,
                    'end': end,
                    'location': event.get('location', ''),
                    'description': event.get('description', '')[:200] if event.get('description') else '',
                    'attendees': [a.get('email') for a in event.get('attendees', [])][:5],
                    'is_all_day': 'date' in event['start']
                })
            
            logger.info(f"Fetched {len(formatted_events)} events for user {user_id}")
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            return [{"error": str(e)}]
        finally:
            db.close()
    
    async def get_today_schedule(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get today's calendar events.
        
        Args:
            user_id: The user's ID
        
        Returns:
            List of today's events
        """
        db = SessionLocal()
        try:
            service = self._get_calendar_service(user_id, db)
            
            # Today's time range
            now = datetime.utcnow()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            time_min = start_of_day.isoformat() + 'Z'
            time_max = end_of_day.isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event.get('summary', '(No title)'),
                    'start': start,
                    'end': end,
                    'location': event.get('location', ''),
                    'is_all_day': 'date' in event['start']
                })
            
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error fetching today's schedule: {e}")
            return [{"error": str(e)}]
        finally:
            db.close()
    
    async def check_availability(
        self, 
        user_id: str, 
        date: str,
        duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Check free time slots on a specific date.
        
        Args:
            user_id: The user's ID
            date: Date to check (YYYY-MM-DD format)
            duration_minutes: Desired meeting duration
        
        Returns:
            Available time slots
        """
        db = SessionLocal()
        try:
            service = self._get_calendar_service(user_id, db)
            
            # Parse date and set time range
            target_date = datetime.strptime(date, '%Y-%m-%d')
            start_of_day = target_date.replace(hour=9, minute=0)  # 9 AM
            end_of_day = target_date.replace(hour=18, minute=0)   # 6 PM
            
            time_min = start_of_day.isoformat() + 'Z'
            time_max = end_of_day.isoformat() + 'Z'
            
            # Get existing events
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Calculate busy times
            busy_times = []
            for event in events:
                if 'dateTime' in event['start']:
                    start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
                    busy_times.append((start, end))
            
            # Find free slots
            free_slots = []
            current_time = start_of_day
            
            for busy_start, busy_end in sorted(busy_times):
                if current_time + timedelta(minutes=duration_minutes) <= busy_start:
                    free_slots.append({
                        'start': current_time.strftime('%H:%M'),
                        'end': busy_start.strftime('%H:%M'),
                        'duration_minutes': int((busy_start - current_time).total_seconds() / 60)
                    })
                current_time = max(current_time, busy_end)
            
            # Check remaining time
            if current_time + timedelta(minutes=duration_minutes) <= end_of_day:
                free_slots.append({
                    'start': current_time.strftime('%H:%M'),
                    'end': end_of_day.strftime('%H:%M'),
                    'duration_minutes': int((end_of_day - current_time).total_seconds() / 60)
                })
            
            return {
                'date': date,
                'free_slots': free_slots,
                'total_free_minutes': sum(slot['duration_minutes'] for slot in free_slots)
            }
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return {"error": str(e)}
        finally:
            db.close()
    
    async def get_next_meeting(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the user's next upcoming meeting.
        
        Args:
            user_id: The user's ID
        
        Returns:
            Next meeting details or None
        """
        events = await self.get_upcoming_events(user_id, days=1, max_results=5)
        
        if events and not events[0].get('error'):
            now = datetime.utcnow()
            for event in events:
                if not event.get('is_all_day'):
                    try:
                        start_time = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                        if start_time > now:
                            return event
                    except:
                        pass
        
        return None


# Global instance
calendar_tools = CalendarTools()
