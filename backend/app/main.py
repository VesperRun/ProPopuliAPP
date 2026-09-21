from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import Base, engine, get_db
from app.gate import evaluate_reply
from app.models import Comment, Hub, Post, User
from app.schemas import (
    CommentCreate,
    CommentPublic,
    GateFailure,
    HubCreate,
    HubPublic,
    LoginRequest,
    PostCreate,
    PostPublic,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)
from app.seed import seed_hubs

app = FastAPI(title="ProPopuli API", version="1.0.0")

from app.config import settings

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
    db = next(get_db())
    try:
        seed_hubs(db)
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "operational", "system": "ProPopuli Core Active"}


@app.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter((User.email == payload.email) | (User.handle == payload.handle)).first():
        raise HTTPException(status_code=400, detail="Email or handle already in use")
    user = User(email=payload.email, handle=payload.handle, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(user.id))


@app.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)):
    return user


@app.get("/hubs", response_model=list[HubPublic])
def list_hubs(db: Session = Depends(get_db)):
    return db.query(Hub).order_by(Hub.name).all()


@app.post("/hubs", response_model=HubPublic, status_code=status.HTTP_201_CREATED)
def create_hub(payload: HubCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if db.query(Hub).filter(Hub.slug == payload.slug).first():
        raise HTTPException(status_code=400, detail="Hub slug already exists")
    hub = Hub(slug=payload.slug, name=payload.name, description=payload.description)
    db.add(hub)
    db.commit()
    db.refresh(hub)
    return hub


@app.get("/hubs/{slug}/posts", response_model=list[PostPublic])
def list_hub_posts(slug: str, db: Session = Depends(get_db)):
    hub = db.query(Hub).filter(Hub.slug == slug).first()
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")
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
    user: User = Depends(get_current_user),
):
    hub = db.query(Hub).filter(Hub.slug == slug).first()
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")
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
    user: User = Depends(get_current_user),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if payload.parent_id is not None:
        parent = db.get(Comment, payload.parent_id)
        if not parent or parent.post_id != post_id:
            raise HTTPException(status_code=400, detail="Invalid parent comment")

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
