from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = "dev-secret-change-me"
    database_url: str = "sqlite:///./propopuli.db"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    cors_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:3001,http://127.0.0.1:3001,"
        "http://localhost:3002,http://127.0.0.1:3002"
    )
    resend_api_key: str | None = None
    resend_from_email: str | None = None
    app_public_url: str = "http://localhost:3000"

    # Comma-separated handles and/or emails — full platform sovereignty (delete subpops, bar, timeout).
    operator_handles: str = ""
    operator_emails: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def operator_handle_set(self) -> set[str]:
        return {h.strip() for h in self.operator_handles.split(",") if h.strip()}

    @property
    def operator_email_set(self) -> set[str]:
        from app.email_util import normalize_email

        out: set[str] = set()
        for raw in self.operator_emails.split(","):
            part = raw.strip()
            if part:
                out.add(normalize_email(part))
        return out


settings = Settings()
