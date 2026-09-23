import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import User

TOKEN_BYTES = 32
RESET_HOURS = 2


def issue_password_reset_token(user: User) -> str:
    token = secrets.token_urlsafe(TOKEN_BYTES)
    user.password_reset_token = token
    user.password_reset_expires_at = datetime.utcnow() + timedelta(hours=RESET_HOURS)
    return token


def consume_password_reset_token(db: Session, token: str) -> User | None:
    user = db.query(User).filter(User.password_reset_token == token.strip()).first()
    if not user:
        return None
    if user.password_reset_expires_at and user.password_reset_expires_at < datetime.utcnow():
        return None
    user.password_reset_token = None
    user.password_reset_expires_at = None
    return user
