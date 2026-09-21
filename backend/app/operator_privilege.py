from fastapi import Depends, HTTPException, status

from app.auth import get_current_user
from app.config import settings
from app.email_util import normalize_email
from app.models import User


def is_operator_user(user: User) -> bool:
    if user.handle in settings.operator_handle_set:
        return True
    if normalize_email(user.email) in settings.operator_email_set:
        return True
    return False


def require_operator(user: User = Depends(get_current_user)) -> User:
    if not is_operator_user(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operator only.")
    return user
