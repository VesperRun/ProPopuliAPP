"""Subpop participation stats (distinct users who posted or commented)."""

from sqlalchemy import text
from sqlalchemy.orm import Session

_PARTICIPANTS_BY_HUB = text(
    """
    SELECT hub_id, COUNT(DISTINCT author_id) AS n
    FROM (
        SELECT hub_id, author_id FROM posts
        UNION
        SELECT p.hub_id, c.author_id
        FROM comments c
        INNER JOIN posts p ON p.id = c.post_id
    )
    GROUP BY hub_id
    """
)


def participant_counts_for_hubs(db: Session) -> dict[int, int]:
    rows = db.execute(_PARTICIPANTS_BY_HUB).mappings().all()
    return {int(r["hub_id"]): int(r["n"]) for r in rows}


_PARTICIPANTS_FOR_HUB = text(
    """
    SELECT COUNT(DISTINCT author_id) AS n
    FROM (
        SELECT author_id FROM posts WHERE hub_id = :hub_id
        UNION
        SELECT c.author_id
        FROM comments c
        INNER JOIN posts p ON p.id = c.post_id
        WHERE p.hub_id = :hub_id
    )
    """
)


def participant_count_for_hub(db: Session, hub_id: int) -> int:
    row = db.execute(_PARTICIPANTS_FOR_HUB, {"hub_id": hub_id}).mappings().first()
    return int(row["n"]) if row else 0
