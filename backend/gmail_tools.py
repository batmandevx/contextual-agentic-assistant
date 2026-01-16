"""
Gmail integration tools for the AI assistant.
Provides functionality to fetch, search, and send emails using Google Gmail API.
"""
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from database import SessionLocal, User, Session as DBSession
from auth import decrypt_token

logger = logging.getLogger(__name__)


class GmailTools:
    """Gmail API tools for the agent."""
    
    def __init__(self):
        """Initialize Gmail tools."""
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.compose'
        ]
    
    def _get_gmail_service(self, user_id: str, db: Session):
        """Get authenticated Gmail service for a user."""
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
            
            # Build Gmail service
            service = build('gmail', 'v1', credentials=credentials)
            return service
            
        except Exception as e:
            logger.error(f"Error getting Gmail service: {e}")
            raise
    
    async def fetch_emails(
        self, 
        user_id: str, 
        max_results: int = 10,
        query: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent emails from user's inbox.
        
        Args:
            user_id: The user's ID
            max_results: Maximum number of emails to fetch
            query: Optional Gmail search query
        
        Returns:
            List of email summaries
        """
        db = SessionLocal()
        try:
            service = self._get_gmail_service(user_id, db)
            
            # Build query
            search_query = query if query else "in:inbox"
            
            # List messages
            results = service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            email_summaries = []
            
            for msg in messages:
                # Get message details
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
                
                email_summaries.append({
                    'id': msg['id'],
                    'from': headers.get('From', 'Unknown'),
                    'subject': headers.get('Subject', '(No subject)'),
                    'date': headers.get('Date', ''),
                    'snippet': message.get('snippet', '')[:100]
                })
            
            logger.info(f"Fetched {len(email_summaries)} emails for user {user_id}")
            return email_summaries
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return [{"error": str(e)}]
        finally:
            db.close()
    
    async def get_email_details(self, user_id: str, email_id: str) -> Dict[str, Any]:
        """
        Get full details of a specific email.
        
        Args:
            user_id: The user's ID
            email_id: The email message ID
        
        Returns:
            Full email content
        """
        db = SessionLocal()
        try:
            service = self._get_gmail_service(user_id, db)
            
            message = service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
            
            # Extract body
            body = ""
            payload = message.get('payload', {})
            
            if 'body' in payload and payload['body'].get('data'):
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            elif 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
            
            return {
                'id': email_id,
                'from': headers.get('From', 'Unknown'),
                'to': headers.get('To', ''),
                'subject': headers.get('Subject', '(No subject)'),
                'date': headers.get('Date', ''),
                'body': body,
                'labels': message.get('labelIds', [])
            }
            
        except Exception as e:
            logger.error(f"Error getting email details: {e}")
            return {"error": str(e)}
        finally:
            db.close()
    
    async def search_emails(
        self, 
        user_id: str, 
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search emails using Gmail query syntax.
        
        Args:
            user_id: The user's ID
            query: Gmail search query (e.g., "from:john subject:meeting")
            max_results: Maximum results to return
        
        Returns:
            List of matching emails
        """
        return await self.fetch_emails(user_id, max_results, query)
    
    async def send_email(
        self, 
        user_id: str,
        to: str,
        subject: str,
        body: str,
        reply_to_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email or reply to an existing email.
        
        Args:
            user_id: The user's ID
            to: Recipient email address
            subject: Email subject
            body: Email body content
            reply_to_id: Optional message ID to reply to
        
        Returns:
            Send result with message ID
        """
        db = SessionLocal()
        try:
            service = self._get_gmail_service(user_id, db)
            
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            message.attach(MIMEText(body, 'plain'))
            
            # If replying, get thread ID
            thread_id = None
            if reply_to_id:
                original = service.users().messages().get(
                    userId='me',
                    id=reply_to_id
                ).execute()
                thread_id = original.get('threadId')
                
                # Get original subject for reply
                headers = {h['name']: h['value'] for h in original.get('payload', {}).get('headers', [])}
                if not subject.lower().startswith('re:'):
                    message['subject'] = f"Re: {headers.get('Subject', '')}"
            
            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            body_data = {'raw': raw}
            if thread_id:
                body_data['threadId'] = thread_id
            
            # Send
            result = service.users().messages().send(
                userId='me',
                body=body_data
            ).execute()
            
            logger.info(f"Email sent successfully: {result.get('id')}")
            return {
                'success': True,
                'message_id': result.get('id'),
                'thread_id': result.get('threadId')
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            db.close()
    
    async def get_important_emails(self, user_id: str, days: int = 3) -> List[Dict[str, Any]]:
        """
        Get important/unread emails from the last N days.
        
        Args:
            user_id: The user's ID
            days: Number of days to look back
        
        Returns:
            List of important emails
        """
        after_date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
        query = f"is:unread OR is:important after:{after_date}"
        return await self.fetch_emails(user_id, max_results=15, query=query)


# Global instance
gmail_tools = GmailTools()
