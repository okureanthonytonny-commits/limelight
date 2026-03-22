from datetime import datetime
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from models import Session as DBSession, User
from database import get_db

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Get current user from session cookie"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Find session
    session = db.query(DBSession).filter(DBSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    # Check if expired
    if session.expires_at < datetime.utcnow():
        # Clean up expired session
        db.delete(session)
        db.commit()
        raise HTTPException(status_code=401, detail="Session expired")

    # Get user
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user