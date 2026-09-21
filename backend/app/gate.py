import json
import re
from dataclasses import dataclass

import httpx

from app.config import settings

SYSTEM_PROMPT = """You classify forum replies for ProPopuli.
Return JSON only: {"pass": boolean, "reasons": string[], "challenge": string}

PASS if the reply is constructive-critical: object-level claim, concrete improvement, or precise question.
FAIL if it is dump/contempt: insults, person-as-target, passive-aggressive dunk, motive-reading, or teardown with no constructive payload.
Blunt but object-level critique should PASS. HR-speak with no substance should FAIL.
On FAIL, challenge must ask the author to restate the objection as an improvement or condition. Do not write their comment for them."""


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


def _heuristic_gate(body: str) -> GateResult:
    text = body.strip()
    lower = text.lower()
    reasons: list[str] = []

    if len(text) < 12:
        reasons.append("Reply is too short to carry a constructive point.")

    for pattern in DUMP_PATTERNS:
        if re.search(pattern, lower, re.I):
            reasons.append("Teardown or contempt phrasing detected.")
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
        "?",
    ]
    if not any(m in lower for m in constructive_markers) and len(text) > 40:
        reasons.append("No object-level improvement, condition, or precise question.")

    if reasons:
        return GateResult(
            passed=False,
            reasons=reasons,
            challenge="Restate your objection as an improvement or a condition (what fails, and what would work instead).",
        )
    return GateResult(passed=True, reasons=[])


async def _openai_gate(body: str, post_title: str, post_body: str) -> GateResult | None:
    if not settings.openai_api_key:
        return None

    user_content = f"Post title: {post_title}\nPost body: {post_body[:2000]}\n\nReply draft:\n{body[:4000]}"

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
                        {"role": "system", "content": SYSTEM_PROMPT},
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
            challenge = "Restate your objection as an improvement or a condition."
        return GateResult(passed=passed, reasons=reasons, challenge=challenge)
    except (httpx.HTTPError, KeyError, json.JSONDecodeError, IndexError):
        return None


async def evaluate_reply(body: str, post_title: str, post_body: str) -> GateResult:
    ai = await _openai_gate(body, post_title, post_body)
    if ai is not None:
        return ai
    return _heuristic_gate(body)
