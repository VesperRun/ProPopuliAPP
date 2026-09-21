from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Comment, Hub, Post, User


def assert_user_can_participate(user: User) -> None:
    if user.banned_permanent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account barred by the operator. Contact support if you believe this is an error.",
        )
    if user.timeout_until and user.timeout_until > datetime.utcnow():
        until = user.timeout_until.strftime("%Y-%m-%d %H:%M UTC")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Timed out until {until}. You can read but not post or reply.",
        )


def delete_subpop_cascade(db: Session, hub: Hub) -> None:
    post_ids = [row[0] for row in db.query(Post.id).filter(Post.hub_id == hub.id).all()]
    if post_ids:
        db.query(Comment).filter(Comment.post_id.in_(post_ids)).delete(synchronize_session=False)
        db.query(Post).filter(Post.hub_id == hub.id).delete(synchronize_session=False)
    db.delete(hub)


def apply_moderation(
    db: Session,
    target: User,
    *,
    action: str,
    hours: int | None,
    note: str,
) -> str:
    if action == "pardon":
        target.banned_permanent = False
        target.timeout_until = None
        target.moderation_note = note or None
        db.commit()
        return f"Pardoned @{target.handle}."

    if action == "bar":
        target.banned_permanent = True
        target.timeout_until = None
        target.moderation_note = note or None
        db.commit()
        return f"Barred @{target.handle} (permanent)."

    if action == "timeout":
        if not hours or hours < 1:
            raise HTTPException(status_code=400, detail="timeout requires hours (1–8760).")
        target.banned_permanent = False
        target.timeout_until = datetime.utcnow() + timedelta(hours=hours)
        target.moderation_note = note or None
        db.commit()
        until = target.timeout_until.strftime("%Y-%m-%d %H:%M UTC")
        return f"Timed out @{target.handle} until {until}."

    raise HTTPException(status_code=400, detail="action must be bar, timeout, or pardon.")
