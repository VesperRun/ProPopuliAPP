import json
import re
from dataclasses import dataclass

import httpx

from app.config import settings

REPLY_SYSTEM_PROMPT = """You classify forum replies for ProPopuli.
Return JSON only: {"pass": boolean, "reasons": string[], "challenge": string}

PASS if the reply is constructive-critical: object-level claim, concrete improvement, or precise question.
FAIL if it is dump/contempt: insults, person-as-target, passive-aggressive dunk, motive-reading, or teardown with no constructive payload.
Blunt but object-level critique should PASS. HR-speak with no substance should FAIL.
On FAIL, challenge must ask the author to restate the objection as an improvement or condition. Do not write their comment for them."""

OPENING_SYSTEM_PROMPT = """You classify opening posts (new fractalpop threads) for ProPopuli.
Return JSON only: {"pass": boolean, "reasons": string[], "challenge": string}

PASS if the post invites structured discourse: clear topic, honest framing, concrete question, or genuine invitation without attacking people.
FAIL if: personal attacks, harassment, rage bait, pile-on invitations, hollow toxic positivity (good-vibes-only, deny harm, spiritual bypass with no substance), or empty hype with no object-level content.
On FAIL, challenge must ask the author to recast title/body as a concrete topic or invitation—not dunk, bait, or hollow positivity. Do not write the post for them."""


@dataclass
class GateResult:
    passed: bool
    reasons: list[str]
    challenge: str | None = None


DUMP_PATTERNS = [
    r"\b(idiot|moron|stupid|trash|garbage|terrible|cope|lmao|lol\b|sure buddy|ok buddy)\b",
    r"\byou('re| are)\s+(wrong|an?\s+\w+)\b",
    r"^\s*(this sucks|worst take)\s*\.?\s*$",
]

TOXIC_POSITIVE_PATTERNS = [
    r"good\s+vibes\s+only",
    r"just\s+(stay\s+)?positive",
    r"no\s+negativity",
    r"negative\s+energy",
    r"everything\s+happens\s+for\s+a\s+reason",
    r"think\s+happy\s+thoughts",
    r"manifest\s+positivity",
    r"toxic\s+positivity",
]

HOSTILE_OPENING_PATTERNS = [
    r"\b(worst|trash|garbage)\s+(take|post|thread|community)\b",
    r"\b(rage|ratio|owned|destroyed)\b",
    r"^\s*@(everyone|all)\s",
]


def _collect_tone_failures(text: str, *, min_len: int) -> list[str]:
    lower = text.strip().lower()
    reasons: list[str] = []

    if len(text.strip()) < min_len:
        reasons.append("Too short to carry a clear, good-faith point.")

    for pattern in DUMP_PATTERNS:
        if re.search(pattern, lower, re.I):
            reasons.append("Teardown or contempt phrasing detected.")
            break

    for pattern in TOXIC_POSITIVE_PATTERNS:
        if re.search(pattern, lower, re.I):
            reasons.append("Hollow or toxic positivity detected—name the issue or invite real discourse.")
            break

    constructive_markers = [
        "because",
        "instead",
        "unless",
        "would be stronger",
        "consider",
        "what if",
        "how does",
        "why does",
        "question",
        "discuss",
        "introduce",
        "welcome",
        "?",
    ]
    if len(text.strip()) > 48 and not any(m in lower for m in constructive_markers):
        reasons.append("No object-level topic, invitation, or precise question.")

    return reasons


def _heuristic_reply(body: str) -> GateResult:
    reasons = _collect_tone_failures(body, min_len=12)
    if reasons:
        return GateResult(
            passed=False,
            reasons=reasons,
            challenge="Restate your objection as an improvement or a condition (what fails, and what would work instead).",
        )
    return GateResult(passed=True, reasons=[])


def _heuristic_opening(title: str, body: str) -> GateResult:
    combined = f"{title.strip()}\n{body.strip()}".strip()
    lower = combined.lower()
    reasons = _collect_tone_failures(combined, min_len=10)

    for pattern in HOSTILE_OPENING_PATTERNS:
        if re.search(pattern, lower, re.I):
            reasons.append("Hostile or baiting thread framing detected.")
            break

    if len(title.strip()) < 3:
        reasons.append("Title too vague to anchor a fractalpop.")

    if reasons:
        return GateResult(
            passed=False,
            reasons=reasons,
            challenge="Recast as a concrete topic or invitation—what you want discussed, not a dunk or hollow positivity.",
        )
    return GateResult(passed=True, reasons=[])


async def _openai_classify(
    system: str,
    user_content: str,
) -> GateResult | None:
    if not settings.openai_api_key:
        return None

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": settings.openai_model,
                    "temperature": 0,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_content},
                    ],
                },
            )
        if resp.status_code != 200:
            return None
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        passed = bool(parsed.get("pass"))
        reasons = [str(r) for r in parsed.get("reasons", [])]
        challenge = parsed.get("challenge")
        if not passed and not challenge:
            challenge = "Recast before you publish."
        return GateResult(passed=passed, reasons=reasons, challenge=challenge)
    except (httpx.HTTPError, KeyError, json.JSONDecodeError, IndexError):
        return None


async def evaluate_reply(body: str, post_title: str, post_body: str) -> GateResult:
    user_content = f"Post title: {post_title}\nPost body: {post_body[:2000]}\n\nReply draft:\n{body[:4000]}"
    ai = await _openai_classify(REPLY_SYSTEM_PROMPT, user_content)
    if ai is not None:
        return ai
    return _heuristic_reply(body)


async def evaluate_opening_post(title: str, body: str) -> GateResult:
    user_content = f"Title: {title[:300]}\nBody: {body[:8000]}"
    ai = await _openai_classify(OPENING_SYSTEM_PROMPT, user_content)
    if ai is not None:
        return ai
    return _heuristic_opening(title, body)
