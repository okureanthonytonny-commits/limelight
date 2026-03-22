import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from config import settings
from database import get_db
from models import Session as DBSession, User

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@router.get('/login')
async def login(request: Request):
    """Redirect to Google OAuth login"""
    redirect_uri = settings.oauth_redirect_uri
    
    # Print session BEFORE redirect
    print(f"Login - session before redirect: {dict(request.session)}")
    
    response = await oauth.google.authorize_redirect(request, redirect_uri)
    
    # After redirect, the session should contain the state
    print(f"Login - session after redirect: {dict(request.session)}")
    return response

@router.get('/callback')
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Handle OAuth callback from Google"""
    try:
        
        token = await oauth.google.authorize_access_token(request)
        logger.info(f"Token obtained: {token.keys()}")

        # Get user info
        user_info = token.get('userinfo')
        if not user_info:
            # Fallback to parsing ID token
            user_info = await oauth.google.parse_id_token(request, token)
        logger.info(f"User info: {user_info}")

        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")

        # Extract user data
        email = user_info.get('email')
        name = user_info.get('name')
        google_id = user_info.get('sub')  # Google's unique user ID

        if not email or not google_id:
            raise HTTPException(status_code=400, detail="Incomplete user info from Google")

        # Check if user exists
        user = db.query(User).filter(User.oauth_id == google_id).first()

        if not user:
            # Create new user
            username = email.split('@')[0]  # Use email prefix as username
            # Ensure username is unique? Not needed for MVP
            user = User(
                username=username,
                password_hash="",  # No password for OAuth users
                oauth_provider="google",
                oauth_id=google_id
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {user.id} - {email}")

        # Create session
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)  # 24 hour session

        db_session = DBSession(
            session_id=session_id,
            user_id=user.id,
            expires_at=expires_at
        )
        db.add(db_session)
        db.commit()
        logger.info(f"Created session for user {user.id}")


        # Set HttpOnly cookie and redirect
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=24*60*60  # 24 hours
        )
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.exception("OAuth callback failed")
        raise HTTPException(status_code=400, detail=f"OAuth callback failed: {str(e)}")

@router.post('/logout')
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """Logout user by clearing session"""
    session_id = request.cookies.get("session_id")
    if session_id:
        # Delete session from DB
        db.query(DBSession).filter(DBSession.session_id == session_id).delete()
        db.commit()
        logger.info(f"Deleted session {session_id}")

    # Clear cookie
    response = Response(content="Logged out")
    response.delete_cookie("session_id")
    return response