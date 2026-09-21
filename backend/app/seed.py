from sqlalchemy.orm import Session

from app.models import Hub


DEFAULT_HUBS = [
    ("general", "General", "Start here. Recast critiques before you publish."),
    ("build", "Build", "Ship work, ask sharp questions, improve ideas."),
]


def seed_hubs(db: Session) -> None:
    for slug, name, description in DEFAULT_HUBS:
        exists = db.query(Hub).filter(Hub.slug == slug).first()
        if not exists:
            db.add(Hub(slug=slug, name=name, description=description))
    db.commit()
