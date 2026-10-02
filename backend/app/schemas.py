from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    handle: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: int
    handle: str
    email: str
    email_verified: bool
    is_operator: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class ModerationRequest(BaseModel):
    action: Literal["bar", "timeout", "pardon"]
    hours: int | None = Field(default=None, ge=1, le=8760)
    note: str = Field(default="", max_length=512)


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=10, max_length=256)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=10, max_length=256)
    password: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str


class ContactPublic(BaseModel):
    admin_email: str | None = None


class HubCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=32, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=2, max_length=128)
    description: str = Field(default="", max_length=512)


class HubPublic(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    participant_count: int = Field(
        default=0,
        description="Distinct users who posted or commented in this subpop.",
    )

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=300)
    body: str = Field(default="", max_length=10000)


class PostPublic(BaseModel):
    id: int
    hub_slug: str
    title: str
    body: str
    author_handle: str
    created_at: datetime
    comment_count: int = 0

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=8000)
    parent_id: int | None = None


class CommentPublic(BaseModel):
    id: int
    post_id: int
    parent_id: int | None
    body: str
    author_handle: str
    created_at: datetime

    class Config:
        from_attributes = True


class GateFailure(BaseModel):
    detail: str
    reasons: list[str]
    challenge: str


ReportCategory = Literal[
    "spam",
    "harassment",
    "illegal",
    "sexual_content",
    "misinformation",
    "other",
]


class ReportCreate(BaseModel):
    category: ReportCategory
    details: str = Field(default="", max_length=2000)


class FeedbackCreate(BaseModel):
    body: str = Field(min_length=10, max_length=4000)
    category: ReportCategory = "other"


class ReportPublic(BaseModel):
    id: int
    kind: str
    category: str
    details: str
    status: str
    post_id: int | None
    comment_id: int | None
    hub_slug: str | None = None
    post_title: str | None = None
    content_excerpt: str | None = None
    target_author_handle: str | None = None
    reporter_handle: str | None = None
    ai_severity: str | None = None
    ai_summary: str | None = None
    ai_recommended_action: str | None = None
    ai_tags: list[str] = []
    created_at: datetime
    resolved_at: datetime | None = None
    resolution_note: str | None = None


class ReportResolveRequest(BaseModel):
    status: Literal["resolved", "dismissed"]
    note: str = Field(default="", max_length=512)
