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

    if not alters:
        return

    with engine.begin() as conn:
        for stmt in alters:
            conn.execute(text(stmt))
        # Grandfather accounts created before verify-email shipped.
        conn.execute(text("UPDATE users SET email_verified = 1 WHERE verification_token IS NULL"))
        conn.execute(text("UPDATE users SET email = LOWER(email) WHERE email != LOWER(email)"))
