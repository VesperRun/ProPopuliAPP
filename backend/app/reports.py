import json
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.content_policy import assert_content_policy
from app.models import Comment, Hub, Post, Report, User
from app.report_triage import triage_report
from app.schemas import ReportPublic


def _tags_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(x) for x in parsed][:12]
    except json.JSONDecodeError:
        pass
    return []


def report_to_public(db: Session, report: Report, *, include_reporter: bool) -> ReportPublic:
    hub_slug = None
    post_title = None
    content_excerpt = None
    target_handle = None

    if report.post_id:
        row = (
            db.query(Post, Hub.slug, User.handle)
            .join(Hub, Post.hub_id == Hub.id)
            .join(User, Post.author_id == User.id)
            .filter(Post.id == report.post_id)
            .first()
        )
        if row:
            post, hub_slug, target_handle = row
            post_title = post.title
            if report.comment_id:
                comment = db.get(Comment, report.comment_id)
                if comment:
                    content_excerpt = comment.body[:800]
                    author = db.get(User, comment.author_id)
                    if author:
                        target_handle = author.handle
            else:
                excerpt = f"{post.title}\n{post.body}".strip()
                content_excerpt = excerpt[:800]

    reporter_handle = None
    if include_reporter:
        reporter = db.get(User, report.reporter_id)
        if reporter:
            reporter_handle = reporter.handle

    return ReportPublic(
        id=report.id,
        kind=report.kind,
        category=report.category,
        details=report.details,
        status=report.status,
        post_id=report.post_id,
        comment_id=report.comment_id,
        hub_slug=hub_slug,
        post_title=post_title,
        content_excerpt=content_excerpt,
        target_author_handle=target_handle,
        reporter_handle=reporter_handle,
        ai_severity=report.ai_severity,
        ai_summary=report.ai_summary,
        ai_recommended_action=report.ai_recommended_action,
        ai_tags=_tags_list(report.ai_tags),
        created_at=report.created_at,
        resolved_at=report.resolved_at,
        resolution_note=report.resolution_note,
    )


def _existing_open_report(
    db: Session,
    reporter_id: int,
    *,
    kind: str,
    post_id: int | None,
    comment_id: int | None,
) -> Report | None:
    q = db.query(Report).filter(
        Report.reporter_id == reporter_id,
        Report.kind == kind,
        Report.status == "open",
    )
    if post_id is not None:
        q = q.filter(Report.post_id == post_id)
    if comment_id is not None:
        q = q.filter(Report.comment_id == comment_id)
    else:
        q = q.filter(Report.comment_id.is_(None))
    return q.first()


async def file_content_report(
    db: Session,
    reporter: User,
    *,
    kind: str,
    post_id: int,
    comment_id: int | None,
    category: str,
    details: str,
) -> Report:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    target_author_id = post.author_id
    content_excerpt = f"{post.title}\n{post.body}"[:4000]

    if comment_id is not None:
        comment = db.get(Comment, comment_id)
        if not comment or comment.post_id != post_id:
            raise HTTPException(status_code=404, detail="Comment not found")
        target_author_id = comment.author_id
        content_excerpt = comment.body[:4000]

    if target_author_id == reporter.id:
        raise HTTPException(status_code=400, detail="You cannot report your own content.")

    dup = _existing_open_report(
        db,
        reporter.id,
        kind=kind,
        post_id=post_id,
        comment_id=comment_id,
    )
    if dup:
        raise HTTPException(
            status_code=409,
            detail="You already have an open report on this content. Moderators will review it.",
        )

    report = Report(
        reporter_id=reporter.id,
        kind=kind,
        post_id=post_id,
        comment_id=comment_id,
        category=category,
        details=details.strip(),
        status="open",
    )
    db.add(report)
    db.flush()

    triage = await triage_report(
        category=category,
        details=details,
        content_excerpt=content_excerpt,
        reporter_note=details,
    )
    report.ai_severity = triage.severity
    report.ai_summary = triage.summary
    report.ai_recommended_action = triage.recommended_action
    report.ai_tags = json.dumps(triage.tags)
    db.commit()
    db.refresh(report)
    return report


async def file_platform_feedback(
    db: Session,
    reporter: User,
    *,
    category: str,
    body: str,
) -> Report:
    assert_content_policy(body)

    report = Report(
        reporter_id=reporter.id,
        kind="platform_feedback",
        post_id=None,
        comment_id=None,
        category=category,
        details=body.strip(),
        status="open",
    )
    db.add(report)
    db.flush()

    triage = await triage_report(
        category=category,
        details=body,
        content_excerpt="(platform feedback — no specific post)",
        reporter_note=body,
    )
    report.ai_severity = triage.severity
    report.ai_summary = triage.summary
    report.ai_recommended_action = triage.recommended_action
    report.ai_tags = json.dumps(triage.tags)
    db.commit()
    db.refresh(report)
    return report


def resolve_report(
    db: Session,
    report: Report,
    resolver: User,
    *,
    status: str,
    note: str,
) -> Report:
    if report.status != "open":
        raise HTTPException(status_code=400, detail="Report is already closed.")
    if status not in ("resolved", "dismissed"):
        raise HTTPException(status_code=400, detail="status must be resolved or dismissed.")
    report.status = status
    report.resolved_at = datetime.utcnow()
    report.resolver_id = resolver.id
    report.resolution_note = note.strip() or None
    db.commit()
    db.refresh(report)
    return report
