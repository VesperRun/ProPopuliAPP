import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import User

TOKEN_BYTES = 32
TOKEN_HOURS = 48


def issue_verification_token(user: User) -> str:
    token = secrets.token_urlsafe(TOKEN_BYTES)
    user.verification_token = token
    user.verification_expires_at = datetime.utcnow() + timedelta(hours=TOKEN_HOURS)
    return token


def verify_token(db: Session, token: str) -> User | None:
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        return None
    if user.verification_expires_at and user.verification_expires_at < datetime.utcnow():
        return None
    user.email_verified = True
    user.verification_token = None
    user.verification_expires_at = None
    db.commit()
    db.refresh(user)
    return user
