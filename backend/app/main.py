from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.auth_deps import require_verified_user
from app.moderation import apply_moderation, delete_subpop_cascade
from app.operator_privilege import is_operator_user, require_operator
from app.config import settings
from app.content_policy import assert_content_policy
from app.email_util import normalize_email
from app.mailer import send_verification_email
from app.migrate import run_migrations
from app.verification import issue_verification_token, verify_token
from app.database import Base, engine, get_db
from app.gate import evaluate_reply
from app.models import Comment, Hub, Post, User
from app.schemas import (
    CommentCreate,
    CommentPublic,
    ContactPublic,
    GateFailure,
    HubCreate,
    HubPublic,
    LoginRequest,
    PostCreate,
    PostPublic,
    MessageResponse,
    ModerationRequest,
    RegisterRequest,
    TokenResponse,
    UserPublic,
    VerifyEmailRequest,
)
from app.seed import seed_hubs

app = FastAPI(title="ProPopuli API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    run_migrations()
    db = next(get_db())
    try:
        seed_hubs(db)
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "operational", "system": "ProPopuli Core Active"}


@app.get("/public/contact", response_model=ContactPublic)
def public_contact():
    email = settings.contact_admin_email.strip()
    return ContactPublic(admin_email=email or None)


def _send_verify(user: User) -> None:
    token = issue_verification_token(user)
    verify_url = f"{settings.app_public_url.rstrip('/')}/verify-email?token={token}"
    send_verification_email(user.email, verify_url)


@app.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = normalize_email(str(payload.email))
    assert_content_policy(payload.handle)
    if db.query(User).filter((User.email == email) | (User.handle == payload.handle)).first():
        raise HTTPException(status_code=400, detail="Email or handle already in use")
    user = User(
        email=email,
        handle=payload.handle,
        password_hash=hash_password(payload.password),
        email_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    _send_verify(user)
    db.commit()
    return TokenResponse(access_token=create_access_token(user.id))


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = normalize_email(str(payload.email))
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.banned_permanent:
        raise HTTPException(status_code=403, detail="Account barred by the operator.")
    return TokenResponse(access_token=create_access_token(user.id))


@app.post("/auth/verify-email", response_model=MessageResponse)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    user = verify_token(db, payload.token.strip())
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")
    return MessageResponse(message="Email verified. You can post and reply.")


@app.post("/auth/resend-verification", response_model=MessageResponse)
def resend_verification(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.email_verified:
        return MessageResponse(message="Email already verified.")
    _send_verify(user)
    db.commit()
    return MessageResponse(message="Verification email sent.")


def _user_public(user: User) -> UserPublic:
    return UserPublic(
        id=user.id,
        handle=user.handle,
        email=user.email,
        email_verified=user.email_verified,
        is_operator=is_operator_user(user),
        created_at=user.created_at,
    )


@app.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)):
    return _user_public(user)


@app.get("/hubs", response_model=list[HubPublic])
def list_hubs(db: Session = Depends(get_db)):
    return db.query(Hub).order_by(Hub.name).all()


@app.post("/hubs", response_model=HubPublic, status_code=status.HTTP_201_CREATED)
def create_hub(payload: HubCreate, db: Session = Depends(get_db), user: User = Depends(require_verified_user)):
    assert_content_policy(payload.slug, payload.name, payload.description)
    if db.query(Hub).filter(Hub.slug == payload.slug).first():
        raise HTTPException(status_code=400, detail="Hub slug already exists")
    hub = Hub(
        slug=payload.slug,
        name=payload.name,
        description=payload.description,
        creator_id=user.id,
    )
    db.add(hub)
    db.commit()
    db.refresh(hub)
    return hub


@app.get("/hubs/{slug}", response_model=HubPublic)
def get_hub(slug: str, db: Session = Depends(get_db)):
    hub = db.query(Hub).filter(Hub.slug == slug).first()
    if not hub:
        raise HTTPException(status_code=404, detail="Subpop not found")
    return hub


@app.get("/hubs/{slug}/posts", response_model=list[PostPublic])
def list_hub_posts(slug: str, db: Session = Depends(get_db)):
    hub = db.query(Hub).filter(Hub.slug == slug).first()
    if not hub:
        raise HTTPException(status_code=404, detail="Subpop not found")
    rows = (
        db.query(Post, User.handle, func.count(Comment.id))
        .join(User, Post.author_id == User.id)
        .outerjoin(Comment, Comment.post_id == Post.id)
        .filter(Post.hub_id == hub.id)
        .group_by(Post.id, User.handle)
        .order_by(Post.created_at.desc())
        .all()
    )
    return [
        PostPublic(
            id=post.id,
            hub_slug=slug,
            title=post.title,
            body=post.body,
            author_handle=handle,
            created_at=post.created_at,
            comment_count=count,
        )
        for post, handle, count in rows
    ]


@app.post("/hubs/{slug}/posts", response_model=PostPublic, status_code=status.HTTP_201_CREATED)
def create_post(
    slug: str,
    payload: PostCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_verified_user),
):
    hub = db.query(Hub).filter(Hub.slug == slug).first()
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")
    assert_content_policy(payload.title, payload.body)
    post = Post(hub_id=hub.id, author_id=user.id, title=payload.title, body=payload.body)
    db.add(post)
    db.commit()
    db.refresh(post)
    return PostPublic(
        id=post.id,
        hub_slug=slug,
        title=post.title,
        body=post.body,
        author_handle=user.handle,
        created_at=post.created_at,
        comment_count=0,
    )


@app.get("/posts/{post_id}", response_model=PostPublic)
def get_post(post_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(Post, Hub.slug, User.handle, func.count(Comment.id))
        .join(Hub, Post.hub_id == Hub.id)
        .join(User, Post.author_id == User.id)
        .outerjoin(Comment, Comment.post_id == Post.id)
        .filter(Post.id == post_id)
        .group_by(Post.id, Hub.slug, User.handle)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    post, hub_slug, handle, count = row
    return PostPublic(
        id=post.id,
        hub_slug=hub_slug,
        title=post.title,
        body=post.body,
        author_handle=handle,
        created_at=post.created_at,
        comment_count=count,
    )


@app.get("/posts/{post_id}/comments", response_model=list[CommentPublic])
def list_comments(post_id: int, db: Session = Depends(get_db)):
    if not db.get(Post, post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    rows = (
        db.query(Comment, User.handle)
        .join(User, Comment.author_id == User.id)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return [
        CommentPublic(
            id=c.id,
            post_id=c.post_id,
            parent_id=c.parent_id,
            body=c.body,
            author_handle=handle,
            created_at=c.created_at,
        )
        for c, handle in rows
    ]


@app.post("/posts/{post_id}/comments", response_model=CommentPublic, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_verified_user),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if payload.parent_id is not None:
        parent = db.get(Comment, payload.parent_id)
        if not parent or parent.post_id != post_id:
            raise HTTPException(status_code=400, detail="Invalid parent comment")

    assert_content_policy(payload.body)
    gate = await evaluate_reply(payload.body, post.title, post.body)
    if not gate.passed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=GateFailure(
                detail="Cognitive friction triggered: restate as constructive critique.",
                reasons=gate.reasons,
                challenge=gate.challenge or "Restate as an improvement or condition.",
            ).model_dump(),
        )

    comment = Comment(
        post_id=post_id,
        author_id=user.id,
        parent_id=payload.parent_id,
        body=payload.body.strip(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return CommentPublic(
        id=comment.id,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        body=comment.body,
        author_handle=user.handle,
        created_at=comment.created_at,
    )


@app.delete("/operator/subpops/{slug}", response_model=MessageResponse)
def operator_delete_subpop(
    slug: str,
    db: Session = Depends(get_db),
    _operator: User = Depends(require_operator),
):
    hub = db.query(Hub).filter(Hub.slug == slug).first()
    if not hub:
        raise HTTPException(status_code=404, detail="Subpop not found")
    delete_subpop_cascade(db, hub)
    db.commit()
    return MessageResponse(message=f"Deleted subpop s\\{slug} and its threads.")


@app.post("/operator/users/{handle}/moderate", response_model=MessageResponse)
def operator_moderate_user(
    handle: str,
    payload: ModerationRequest,
    db: Session = Depends(get_db),
    operator: User = Depends(require_operator),
):
    target = db.query(User).filter(User.handle == handle).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == operator.id and payload.action in ("bar", "timeout"):
        raise HTTPException(status_code=400, detail="You cannot bar or timeout your operator account.")
    if is_operator_user(target) and payload.action in ("bar", "timeout"):
        raise HTTPException(status_code=400, detail="Cannot bar or timeout another operator account.")
    msg = apply_moderation(
        db,
        target,
        action=payload.action,
        hours=payload.hours,
        note=payload.note.strip(),
    )
    return MessageResponse(message=msg)
