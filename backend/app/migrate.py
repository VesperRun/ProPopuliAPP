from sqlalchemy import inspect, text

from app.database import engine


def run_migrations() -> None:
    insp = inspect(engine)
    if "users" not in insp.get_table_names():
        return

    cols = {c["name"] for c in insp.get_columns("users")}
    alters: list[str] = []
    if "email_verified" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0 NOT NULL")
    if "verification_token" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN verification_token VARCHAR(128)")
    if "verification_expires_at" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN verification_expires_at DATETIME")
    if "password_reset_token" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN password_reset_token VARCHAR(128)")
    if "password_reset_expires_at" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN password_reset_expires_at DATETIME")

    hub_alters: list[str] = []
    if "hubs" in insp.get_table_names():
        hub_cols = {c["name"] for c in insp.get_columns("hubs")}
        if "creator_id" not in hub_cols:
            hub_alters.append("ALTER TABLE hubs ADD COLUMN creator_id INTEGER REFERENCES users(id)")

    if "banned_permanent" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN banned_permanent BOOLEAN DEFAULT 0 NOT NULL")
    if "timeout_until" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN timeout_until DATETIME")
    if "moderation_note" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN moderation_note VARCHAR(512)")

    if not alters and not hub_alters:
        return

    with engine.begin() as conn:
        for stmt in alters + hub_alters:
            conn.execute(text(stmt))
        if "email_verified" in {c["name"] for c in insp.get_columns("users")}:
            conn.execute(text("UPDATE users SET email_verified = 1 WHERE verification_token IS NULL"))
            conn.execute(text("UPDATE users SET email = LOWER(email) WHERE email != LOWER(email)"))
