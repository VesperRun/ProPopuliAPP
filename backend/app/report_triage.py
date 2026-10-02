import json
import re
from dataclasses import dataclass

import httpx

from app.config import settings

REPORT_TRIAGE_SYSTEM = """You triage user-submitted reports for ProPopuli, a text forum.
Return JSON only:
{"severity": "low"|"medium"|"high"|"critical", "summary": string, "recommended_action": string, "tags": string[]}

severity guide:
- critical: CSAM or sexual content involving minors, credible threats of violence, trafficking, sale of hard drugs or weapons, extortion
- high: illegal solicitation, non-consensual sexual content, targeted harassment campaigns, doxxing
- medium: spam scams, hate speech, aggressive harassment, explicit sexual content between adults
- low: rude tone, minor spam, off-topic, disputed but not policy-clear

summary: 1-2 sentences for a human moderator.
recommended_action: e.g. "review and remove if confirmed", "bar account", "dismiss as disagreement", "escalate to operator immediately".
tags: short labels like "harassment", "illegal", "spam".

You assist human moderators only; do not claim legal conclusions."""

_CRITICAL = re.compile(
    r"\b("
    r"cp\b|child\s+porn|underage|minor\s+sex|"
    r"kill\s+you|bomb\s+threat|"
    r"human\s+traffick|"
    r"fentanyl\s+for\s+sale|sell\s+guns\s+illeg"
    r")\b",
    re.I,
)
_HIGH = re.compile(
    r"\b("
    r"onlyfans\s+link|escort\s+service|sugar\s+baby|"
    r"doxx|leak\s+address|"
    r"scam\s+wire|crypto\s+doubl"
    r")\b",
    re.I,
)


@dataclass
class TriageResult:
    severity: str
    summary: str
    recommended_action: str
    tags: list[str]


def _heuristic_triage(
    *,
    category: str,
    details: str,
    content_excerpt: str,
) -> TriageResult:
    blob = f"{category}\n{details}\n{content_excerpt}".lower()
    tags = [category]
    if category in ("illegal", "sexual_content"):
        tags.append("policy-sensitive")

    if _CRITICAL.search(blob):
        return TriageResult(
            severity="critical",
            summary="Automated scan flagged potentially critical policy content; human review required immediately.",
            recommended_action="Escalate to operator immediately; preserve content and reporter record.",
            tags=tags + ["auto-critical"],
        )
    if _HIGH.search(blob) or category in ("illegal", "sexual_content"):
        return TriageResult(
            severity="high",
            summary=f"Report category “{category}” with possible high-risk signals; prioritize human review.",
            recommended_action="Review thread, remove if confirmed, consider timeout or bar.",
            tags=tags + ["auto-high"],
        )
    if category in ("harassment", "spam"):
        return TriageResult(
            severity="medium",
            summary=f"User report: {category}. Review context and apply moderation if warranted.",
            recommended_action="Review and remove or warn if confirmed; otherwise dismiss.",
            tags=tags,
        )
    return TriageResult(
        severity="low",
        summary="Standard report queued for moderator review.",
        recommended_action="Review when convenient; dismiss if good-faith disagreement.",
        tags=tags,
    )


async def triage_report(
    *,
    category: str,
    details: str,
    content_excerpt: str,
    reporter_note: str,
) -> TriageResult:
    user_content = (
        f"Report category: {category}\n"
        f"Reporter details: {details[:2000]}\n"
        f"Reported content excerpt:\n{content_excerpt[:4000]}\n"
        f"Additional note: {reporter_note[:1000]}"
    )
    if settings.openai_api_key:
        ai = await _openai_triage(user_content)
        if ai is not None:
            return ai
    return _heuristic_triage(category=category, details=details, content_excerpt=content_excerpt)


async def _openai_triage(user_content: str) -> TriageResult | None:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": settings.openai_model,
                    "temperature": 0,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": REPORT_TRIAGE_SYSTEM},
                        {"role": "user", "content": user_content},
                    ],
                },
            )
        if resp.status_code != 200:
            return None
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        severity = str(parsed.get("severity", "medium")).lower()
        if severity not ("low", "medium", "high", "critical"):
            severity = "medium"
        tags = [str(t) for t in parsed.get("tags", [])][:12]
        return TriageResult(
            severity=severity,
            summary=str(parsed.get("summary", "AI triage completed."))[:2000],
            recommended_action=str(parsed.get("recommended_action", "Human review."))[:1000],
            tags=tags,
        )
    except (httpx.HTTPError, KeyError, json.JSONDecodeError, IndexError, TypeError):
        return None
