# ProPopuli fragility remediation plan

**Purpose:** Close the gaps between local product quality, production hosting, policy (AUP), and moderation—without expanding scope into DMs, meme hosting, or full AI until chosen.

**Related docs:** [acceptable-use-policy.md](./acceptable-use-policy.md), [ai-wrapper-plan.md](./ai-wrapper-plan.md), [hierarchy.md](./hierarchy.md)

---

## Fragility → remediation map

| Fragility | Remediation track | Phase |
|-----------|-------------------|-------|
| Hosting topology (API-only on Render, no web, deploy drift) | **Track A** — Production topology | **1** |
| Enforcement lags policy (no `/policy`, signup assent, report UI, operator queue) | **Track B** — Policy in product + reports UX | **2** |
| Gate scope vs UX copy (replies-only messaging) | **Track C** — Copy & Gate alignment | **2** (parallel) |
| Moderation scale untested (no precedents, contact ≠ report API) | **Track D** — Operator playbook + feedback path | **3** |
| Promo/meme rules policy-only | **Track E** — Heuristic Gate extensions | **3** (optional) |
| AI duplication / accidental cloud calls | **Track F** — Wrapper (defer until AI on) | **4** |

---

## Phase 1 — Production topology (Track A)

**Exit criteria:** Phone and laptop open the **same** GUI URL; API and web both deploy from **`main`**; health + `/hubs` show current features (`participant_count`, grid).

### A1. Create Render **Web Service** (Node)

| Setting | Value |
|---------|--------|
| Repo | `VesperRun/ProPopuliAPP`, branch `main` |
| Name | `propopuli-web` (or similar; **not** the Python service) |
| Root directory | `frontend` |
| Runtime | Node |
| Build | `npm install && npm run build` |
| Start | `npm start` |

**Environment (web):**

- `NEXT_PUBLIC_API_URL` = `https://propopuli-api.onrender.com` (no trailing slash)

Redeploy web after **any** change to this var (build-time for rewrites + `api.js`).

### A2. Harden **API** service (`propopuli-api`)

| Setting | Value |
|---------|--------|
| Root directory | `backend` |
| Start | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

**Environment (API):**

- `SECRET_KEY`, `DATABASE_URL` (Postgres on Render)
- `CORS_ORIGINS` = `https://propopuli-web.onrender.com` (comma-separate; add Porkbun domain later)
- `CONTACT_ADMIN_EMAIL` (optional, for contact page)
- `OPENAI_API_KEY` **unset** (heuristic-only until Track F)
- Operator flags per existing `config` (operator email/handle)

**Action:** Manual Deploy **latest `main`** on API (replace stale commits e.g. `a1dad23`).

### A3. Deploy discipline

- [ ] Enable **Auto-Deploy** on both services for `main`.
- [ ] Document in README or `docs/deploy-render.md`: two services, env vars, “restart ≠ redeploy” for web.
- [ ] Smoke script (manual checklist):
  - `GET https://propopuli-api.onrender.com/health`
  - `GET https://propopuli-api.onrender.com/hubs` → 51-ish hubs, `participant_count` present
  - Open `https://propopuli-web.onrender.com/hubs` → grid layout, sections Platform / corridor

### A4. Porkbun (later, non-blocking)

- [ ] Buy domain; Render web → Custom Domains.
- [ ] Porkbun DNS → CNAME/ALIAS per Render.
- [ ] Append `https://yourdomain.com` to `CORS_ORIGINS`; redeploy **API**.
- [ ] Optional: redirect `.onrender.com` to custom domain.

**Phase 1 done when:** You stop using `localhost` as the “real” demo for others; external URL matches local grid + data.

---

## Phase 2 — Policy & trust surface (Tracks B + C)

**Exit criteria:** New user can read AUP; register acknowledges it; any reader can report a post/comment; operator can see queue in UI.

### B1. Public policy route

- [ ] Add `frontend/app/policy/page.js` — render AUP (import markdown at build time, or static JSX summary + link to full doc on GitHub/raw, or copy “lite” sections from AUP §1–§6).
- [ ] Footer / Nav link: **Policy** → `/policy`.
- [ ] Home + hubs meta line: “Posts, replies, and new subpops pass the Gate” (not replies-only).

**Files:** `frontend/components/Nav.js`, `frontend/app/page.js`, new `policy/page.js`.

### B2. Signup assent

- [ ] Register form: checkbox “I agree to the Acceptable Use Policy” (required), link to `/policy`.
- [ ] Optional backend: store `accepted_aup_at` on `User` (migration + register handler)—**recommended** for appeals; else honor-system checkbox only.

**Files:** `frontend/app/register/page.js`, `backend/app/models.py`, `backend/app/migrate.py`, `backend/app/main.py` register route.

### B3. Report content (posts & comments)

- [ ] Component `ReportDialog` — reason dropdown + optional note; calls:
  - `POST /posts/{id}/report`
  - `POST /comments/{id}/report`
- [ ] Wire on `frontend/app/p/[id]/page.js` (flag on opening sample + each comment branch).
- [ ] Auth: logged-in + verified (match post API); guest → auth wall or “sign in to report”.

**Files:** new `components/ReportDialog.js`, `p/[id]/page.js`; schemas already exist.

### B4. Platform feedback

- [ ] Add `frontend/app/feedback/page.js` OR extend `contact/page.js` with form → `POST /feedback` (authenticated).
- [ ] Keep mailto as fallback for guests on `/contact`.

**Files:** `contact/page.js` or `feedback/page.js`, Nav link.

### B5. Operator report queue

- [ ] Section on `frontend/app/operator/page.js`:
  - `GET /operator/reports` — list open first, show `ai_severity`, `ai_summary`, kind, target ids.
  - `PATCH /operator/reports/{id}` — resolve / dismiss + note.
- [ ] Empty state copy when queue clear.

**Files:** `operator/page.js` only (API exists).

### C1. Gate copy audit (parallel with B)

Replace “replies only” muscle memory everywhere:

| Location | Change |
|----------|--------|
| `frontend/components/AuthWall.js` | Gate applies to **posts and replies** (and subpop create if authed) |
| `frontend/app/p/[id]/page.js` | Auth wall message for **new fractalpop** if read-only path exists |
| `frontend/app/page.js` | Opening posts + replies |
| `README.md` MVP flow | Already partially updated; step 3–4 mention opening post Gate |
| `GateChallenge.js` | Optional: one line “Applies to this sample before publish.” |

**Phase 2 done when:** AUP is reachable, register requires ack, flag works on a test thread, operator sees a test report.

---

## Phase 3 — Moderation readiness (Tracks D + E)

**Exit criteria:** Operator has written precedents; promo spam gets challenged; contact/report paths are distinct and documented.

### D1. Operator playbook (internal doc)

- [ ] Add `docs/moderation-playbook.md`:
  - Severity rubric (align with `report_triage` heuristic labels).
  - 5–10 **example decisions** (satire vs harassment, promo vs contextual link, dismiss vs timeout).
  - When to delete sample vs bar account vs remove subpop.
  - Link to AUP §5.3, §5.5, §10 examples.

No code required; reduces “scale untested” anxiety.

### D2. Report reasons ↔ AUP

- [ ] Align `ReportCreate` reason enums (if any) with playbook categories; surface same labels in `ReportDialog`.

**Files:** `backend/app/schemas.py`, `ReportDialog`.

### D3. Contact vs feedback vs abuse

- [ ] `/contact` — public, email-oriented, general.
- [ ] `/feedback` — authenticated platform feedback → API.
- [ ] In-app **Report** — content-specific → operator queue.

Document in playbook and policy §6.

### E1. Promo heuristics (AUP §5.5 in Gate)

- [ ] In `gate.py` `_heuristic_*` for **opening** samples: optional fail/challenge when:
  - ≥2 URLs and CTA phrases (`sign up`, `% off`, `limited time`, `my saas`, `check out my`, etc.), or
  - body length &lt; N and &gt;50% looks like link list.
- [ ] **Do not** fail single contextual links (AUP OK cases).
- [ ] Mirror patterns in frontend only if pre-check desired (optional).

### E2. Meme / media (policy enforcement without uploads)

- [ ] Heuristic: samples that are **only** a URL to known image hosts (imgur, giphy, tenor, i.redd.it) with &lt;20 chars text → challenge “Text-first policy; add argument in words.”
- [ ] No upload UI; keeps AUP §5.4 honest.

**Phase 3 done when:** Test promo post gets 422/challenge; playbook exists; one real report exercised end-to-end.

---

## Phase 4 — Interaction & AI (after 1–3 stable)

**Not required to fix fragility; listed for refinement order.**

### G1. @mention streamline (AUP §6)

- [ ] Parse `@handle` in post/comment body (display link to profile or search—profile optional).
- [ ] Optional: email notify mentioned user (Resend already in stack for verify/reset).

### G2. Unified OpenAI wrapper (Track F)

- [ ] Implement per [ai-wrapper-plan.md](./ai-wrapper-plan.md) **only when** turning AI on.
- [ ] Until then: verify `OPENAI_API_KEY` absent in Render API env.

---

## Suggested execution order (single builder)

```text
Week A — Phase 1 (Render web + API deploy + smoke)
Week B — Phase 2 B1–B3 (policy page, register, report on threads)
Week C — Phase 2 B4–B5 + Track C copy audit
Week D — Phase 3 D1–D3 + E1 (playbook + promo heuristic)
Defer — Porkbun, mentions, AI wrapper, meme URL heuristic (E2) if time tight
```

---

## Verification checklist (full remediation)

- [ ] **A:** Two Render services; web URL shows grid; API on latest `main`.
- [ ] **B:** `/policy`, register checkbox, report on post/comment, operator reports UI, feedback form.
- [ ] **C:** No user-facing copy says Gate is reply-only.
- [ ] **D:** `docs/moderation-playbook.md` with examples.
- [ ] **E:** Promo heuristic live in `gate.py` (optional E2 meme-link challenge).

---

## Out of scope (explicit)

- Private DMs, image/GIF hosting, paid ads product, statewide subreddit clone, full PV compliance refactor.

---

*Update this doc when a phase completes; link PRs or commit hashes in Render deploy notes if helpful.*
