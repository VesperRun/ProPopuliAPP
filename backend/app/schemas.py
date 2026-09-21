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


class MessageResponse(BaseModel):
    message: str


class HubCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=32, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=2, max_length=128)
    description: str = Field(default="", max_length=512)


class HubPublic(BaseModel):
    id: int
    slug: str
    name: str
    description: str

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
