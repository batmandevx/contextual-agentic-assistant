"""
Authentication module for Google OAuth 2.0 and session management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from jose import JWTError, jwt
import base64
import logging

from config import settings
from database import get_db, User, Session as DBSession

logger = logging.getLogger(__name__)
router = APIRouter()

# Encryption for tokens
def get_cipher():
    """Get Fernet cipher for token encryption."""
    key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32].ljust(32, b'0'))
    return Fernet(key)


def encrypt_token(token: str) -> str:
    """Encrypt a token."""
    cipher = get_cipher()
    return cipher.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token."""
    cipher = get_cipher()
    return cipher.decrypt(encrypted_token.encode()).decode()


# OAuth flow configuration
def get_oauth_flow():
    """Create OAuth flow for Google authentication."""
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.compose",
            "https://www.googleapis.com/auth/calendar.readonly"
        ],
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )


def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


@router.post("/login")
async def login():
    """Initiate Google OAuth login flow."""
    try:
        flow = get_oauth_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return {"redirect_url": authorization_url, "state": state}
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate login"
        )


@router.get("/callback")
async def auth_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle OAuth callback from Google."""
    try:
        # Exchange code for tokens
        flow = get_oauth_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Verify ID token
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        # Extract user info
        google_id = id_info['sub']
        email = id_info['email']
        name = id_info.get('name', '')
        
        # Get or create user
        user = db.query(User).filter(User.google_id == google_id).first()
        if not user:
            user = User(
                google_id=google_id,
                email=email,
                name=name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {email}")
        else:
            # Update user info
            user.email = email
            user.name = name
            user.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"User logged in: {email}")
        
        # Encrypt and store tokens
        access_token_encrypted = encrypt_token(credentials.token)
        refresh_token_encrypted = encrypt_token(credentials.refresh_token or "")
        
        # Create session
        expires_at = datetime.utcnow() + timedelta(hours=1)
        session = DBSession(
            user_id=user.id,
            access_token_encrypted=access_token_encrypted,
            refresh_token_encrypted=refresh_token_encrypted,
            expires_at=expires_at
        )
        db.add(session)
        db.commit()
        
        # Create JWT for frontend
        jwt_token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "session_id": str(session.id)
        })
        
        # Redirect to frontend with token
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={jwt_token}"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"Auth callback error: {e}", exc_info=True)
        error_url = f"{settings.FRONTEND_URL}/auth/error?message=Authentication failed"
        return RedirectResponse(url=error_url)


@router.post("/logout")
async def logout(token: str, db: Session = Depends(get_db)):
    """Logout user and revoke session."""
    try:
        payload = verify_token(token)
        session_id = payload.get("session_id")
        
        if session_id:
            session = db.query(DBSession).filter(DBSession.id == session_id).first()
            if session:
                db.delete(session)
                db.commit()
                logger.info(f"Session {session_id} deleted")
        
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/status")
async def auth_status(token: str, db: Session = Depends(get_db)):
    """Check authentication status."""
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "authenticated": True,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth status error: {e}")
        return {"authenticated": False}


# Dependency for getting current user
async def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    """Get current authenticated user."""
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
