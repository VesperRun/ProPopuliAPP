from fastapi import Depends, HTTPException, status

from app.auth import get_current_user
from app.moderation import assert_user_can_participate
from app.models import User


def require_active_user(user: User = Depends(get_current_user)) -> User:
    assert_user_can_participate(user)
    return user


def require_verified_user(user: User = Depends(require_active_user)) -> User:
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verify your email before posting or replying. Check your inbox or resend from account settings.",
        )
    return user
