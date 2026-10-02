# Future: unified OpenAI wrapper (not implemented)

**Operational choice (now):** Keep ProPopuli **heuristically gated**. Leave `OPENAI_API_KEY` **unset** in `backend/.env` and in production secrets. The Reframing Gate and report triage then use **local rules only**—no outbound model calls.

When/if you want classifier + challenge from a model again, implement the wrapper below instead of duplicating `httpx` calls.

---

## Current state (as of 2026)

| Surface | File | Behavior |
|---------|------|----------|
| Reframing Gate (threads, replies, user-created subpops) | [`backend/app/gate.py`](../backend/app/gate.py) | `_openai_classify()` if key set; else `_heuristic_*` |
| Report / feedback triage (operator queue) | [`backend/app/report_triage.py`](../backend/app/report_triage.py) | `_openai_triage()` if key set; else `_heuristic_triage` |
| Config | [`backend/app/config.py`](../backend/app/config.py) | `openai_api_key`, `openai_model` (default `gpt-4o-mini`) |

There is **no** shared client module. Prompts, JSON parsing, timeouts, and failure handling are **copy-pasted** in two places.

Frontend **never** calls OpenAI; only the backend may, and only when the key is present.

---

## Goals for a “real wrapper”

1. **Single module** (e.g. `backend/app/openai_client.py` or `ai_wrapper.py`) for all JSON-classification calls.
2. **Explicit policy flag** (e.g. `AI_ENABLED=true` plus key) so heuristic-only deploys cannot accidentally hit the API.
3. **Consistent contract:** `async def classify_json(*, system: str, user: str, timeout_s: float) -> dict | None` — `None` → callers use heuristics (same as today on failure).
4. **One place** for model name, timeout, token limits, and safe logging (no raw user content in logs in production).
5. **Callers stay thin:** `gate.py` and `report_triage.py` keep prompts + heuristic fallbacks; they only swap `_openai_*` for the shared client.

---

## Proposed implementation sketch

```text
backend/app/openai_client.py
  - settings: openai_api_key, openai_model, ai_enabled (default False)
  - async classify_json(system, user) -> dict | None
  - Never raise to callers; return None on missing key, disabled flag, HTTP error, or bad JSON

gate.py
  - evaluate_reply / evaluate_opening_post: ai = await classify_json(...); map JSON to GateResult

report_triage.py
  - triage_report: ai = await classify_json(...); map JSON to TriageResult

Optional later
  - Pre-publish content policy pass (high-severity categories only, human-in-the-loop)
  - Rate limit per user for any AI-backed path
```

---

## Product rules to preserve when wiring the wrapper

- **Gate:** Fail closed on **tone/teardown** (recast challenge), not on legal verdicts. AI assists classification; heuristics remain the default path when wrapper returns `None`.
- **Reports:** AI output is **advisory** (`ai_severity`, `ai_summary`, `ai_recommended_action`) for operators; **no** auto-delete or auto-bar from model output alone.
- **Secrets:** Key stays in backend env / host secrets only; never `NEXT_PUBLIC_*` or frontend.

---

## Related work (separate from the wrapper)

These were discussed but are not blocked on the wrapper:

- Report / flag **UI** (thread page, `/feedback`, operator report queue in [`frontend/app/operator/page.js`](../frontend/app/operator/page.js)) — backend routes exist under `/feedback`, `/posts/{id}/report`, `/operator/reports`.
- Terms / AUP at signup, CSAM reporting playbook (legal/ops, not code in this doc).

---

## Checklist when you decide to implement

- [ ] Add `openai_client.py` + `AI_ENABLED` (or rely solely on empty key).
- [ ] Refactor `gate.py` and `report_triage.py` to use it; delete duplicate `httpx` blocks.
- [ ] Document in [`README.md`](../README.md): heuristic default vs enabling AI.
- [ ] Smoke-test: key unset → 100% heuristic; key set + enabled → Gate and report triage get JSON paths.
- [ ] Optional: integration test with mocked HTTP (no live API in CI).
