# ProPopuli Acceptable Use Policy (AUP)

**Status:** Living document (v1.0)  
**Copyright © 2026 VesperRun.** Proprietary. Applies to all use of the ProPopuli **pop** (platform), **subpops**, **fractalpops**, and **samples** (posts and replies). See [hierarchy.md](./hierarchy.md) for terms.

---

## 1. Spirit of the house

ProPopuli is a public forum for **argument that can survive a mirror**: satire, skepticism, and plain speech are welcome; **performance without substance** is not.

The platform is informed by a simple ethic (not a loyalty test):

- **Lucian of Samosata** — wit and dialogue expose pretense; comedy is allowed when it targets ideas and posturing, not random cruelty.
- **Diogenes & Hipparchia** — strip the costume; say what you mean in the open; do not hide behind brands, alts, or back channels when the conversation belongs in public.
- **Philosophia Vesperi / Codis Narcissi** — structure and honest reflection over flattery; the **Reframing Gate** challenges *form* (teardown, bait, hollow noise), not every disagreement.

We design for the **mathematical mean**: most threads are quiet, some are sharp, a few are bad. Policy and moderation exist for the tail, not to flatten every edge.

---

## 2. What ProPopuli is for

| In scope | Out of scope (use elsewhere or not at all) |
|----------|---------------------------------------------|
| Local and platform discussion in **subpops** (`s\slug`) | Private commerce, hookups, or illegal markets as **subpop themes** |
| **Fractalpops** — one topic, nested **branches** (replies) | Coordinated harassment campaigns |
| Constructive conflict, satire, civic and build talk | Doxxing, threats, sexual exploitation, CSAM |
| Handles and public samples | Impersonation, spam factories, undisclosed astroturf |

**Interaction model (default):** conversation happens in **public fractalpops**. Direct user-to-user messaging is not a core feature; address others with **`@handle`** inside threads unless a future product explicitly adds private channels under this policy.

---

## 3. Accounts and identity

- Register with a valid email; use a **public handle** (3–32 characters). **Do not** post legal names, home addresses, phone numbers, or third-party private identifiers unless you have consent and a compelling public reason (rare).
- One person may hold one primary account unless the **operator** approves an exception (e.g. org account).
- **Operator** accounts (env-configured) may remove subpops and apply account **bar**, **timeout**, or **pardon** after review.
- Verify email before creating subpops or publishing samples that require verification.

---

## 4. Subpops (hubs)

### 4.1 Creating subpops

- Slugs: lowercase letters, numbers, hyphens; 2–32 characters. Display as **s\slug**.
- Names and descriptions must not violate **hub policy** (automated): no porn/sexual-hook-up niches, obvious illegal markets, or leetspeak evasions of those rules.
- New subpops pass the **Reframing Gate** on name/description — invitation to a niche, not bait or empty hype.

### 4.2 Fit

Pick an existing subpop when possible. Create a new one when the topic is distinct and durable. Corridor and platform subpops are seeded for Austin–San Antonio and cross-cutting topics; community-created subpops appear separately in the directory.

### 4.3 Operator removal

Only the **operator** may delete a subpop (cascade). Abuse of subpop creation (spam niches, policy evasion) may lead to account moderation.

---

## 5. Samples — posts and replies

A **sample** is an opening post (title + body) or a **reply** in a branch.

### 5.1 Reframing Gate

Automated **Gate** runs on:

- new subpop name/description,
- new opening posts,
- replies.

If a sample reads as **teardown, bait, or hollow positivity** without a recast path, publication may be blocked (**422**) with a **challenge** to rewrite. Disagreement is allowed; **unproductive destruction** is not.

When `OPENAI_API_KEY` is unset, heuristics enforce the same intent locally.

### 5.2 Hard-prohibited content (automated block)

Including but not limited to:

- credible threats of violence, severe harassment slurs, and self-harm encouragement (see server **hard block** list),
- naming or echoing certain competitor platform branding where policy forbids it,
- illegal content (CSAM, credible threats, facilitation of serious crime).

**No system is perfect.** Report violations; operators review.

### 5.3 Satire, cynicism, and ridicule

**Allowed** when:

- the target is **ideas, public figures in their public role, or your own side** — not random users’ dignity,
- a reasonable reader can tell **good-faith send-up** from harassment,
- subpop culture fits (e.g. send-up, civic debate) and samples stay within Gate and hard blocks.

**Not allowed:**

- slurs, dehumanization, or “it’s just a joke” as cover for targeting protected groups or individuals,
- brigading a user across fractalpops.

When in doubt: **steel the opposing view in one sentence**, then satirize — Lucian’s dialogue, not a drive-by.

### 5.4 Media — text first

**Default (v1):**

- Samples are **text**. ProPopuli does **not** host images, GIFs, memes, or video uploads.
- Do not use the platform primarily to circulate meme dumps or reaction-GIF threads.

**Links:** plain URLs in text may appear when they **support the argument** (see §6). ProPopuli does not guarantee link previews or embeds; no autoplay media.

**Future change:** If inline media is ever allowed, it will be **explicitly announced**, likely restricted to named subpops, and subject to this AUP and moderation load.

### 5.5 Promotion and links

| Generally OK | Generally not OK |
|--------------|------------------|
| One or few **contextual** links (docs, source, map, tool you used) | Sample whose **main purpose** is advertising a product, SaaS, course, or service |
| Brief mention “I work on X; here’s the doc link” in a **relevant** thread | Copy-pasted **launch posts** cross-posted to many subpops |
| Hiring or classifieds in **fitting** subpops (e.g. hiring, swap) | Affiliate funnels, referral spam, SEO garbage |
| Sharing your **ship log** in `s\ship-log` or build-related subpops | Disguised ads without disclosure in general/civic threads |

**Rule of thumb:** *Link + your analysis in the same sample* → conversation. *Sample = marketing brochure* → rewrite, move to an appropriate subpop, or omit.

Undisclosed paid or incentivized promotion may be treated as spam.

### 5.6 Privacy and safety

- No doxxing, stalking, or encouraging others to contact someone off-platform against their will.
- No sexual content involving minors; zero tolerance, report to operator and authorities as applicable.
- No facilitation of illegal drug sales, weapons trafficking, fraud, or stolen data.

---

## 6. User-to-user conduct

- **Debate the sample, not the person.** Handles are public; cruelty as sport is out.
- **@handle** (when supported in UI) should identify who you answer; don’t tag users to pile on.
- **Reports:** use **Flag / Report** on posts and replies, or **platform feedback**, when automation or mods should see it. False reporting in bad faith may be moderated.
- **Operator queue:** reports may receive automated **triage** (severity/summary); humans decide outcomes.

Preferred order of escalation: **rewrite (Gate)** → **report** → **operator action** → **account bar/timeout**.

Private messaging, if added later, will ship with rate limits, reporting, and the same AUP; it is not a bypass for harassment.

---

## 7. Enforcement ladder

| Layer | What it does |
|-------|----------------|
| **Hub policy** | Blocks disallowed subpop names/descriptions at creation |
| **Content policy** | Hard blocks and banned wording |
| **Reframing Gate** | Blocks or challenges unproductive samples before publish |
| **Community reports** | Queue for operator review (+ optional AI triage summary) |
| **Operator moderation** | Delete content, remove subpop, timeout, permanent bar, pardon |

Moderation notes may be stored on accounts (operator-only detail). Decisions should be **proportionate**; permanent bar for repeat or severe harm.

---

## 8. Legal and platform rights

- You retain rights in your samples; you grant ProPopuli a license to host and display them as needed to operate the service.
- ProPopuli may remove content, suspend access, or cooperate with law enforcement when required by law or imminent harm.
- Service provided **as-is**; no guarantee of uptime, retention, or error-free Gate judgments.
- Contact: public **Contact** route / operator email configured for the deployment.

---

## 9. Changes

The operator may update this AUP. Material changes should be reflected in product copy (signup, footer, or `/policy`) when wired in the app. Continued use after notice constitutes acceptance where applicable.

---

## 10. Quick reference — examples

**OK**

- “Your zoning take ignores renters; here’s the city PDF: `https://…`”
- “I ship weekly; this week: fixed auth bug (details in thread)” in `s\ship-log`
- Good-natured Austin send-up that doesn’t name a private individual

**Not OK**

- “Sign up for my SaaS — 50% off” as the opening post in `s\general`
- Meme-only reply chains with no text argument
- Subpop slug `hookups-austin` or descriptions evading hub policy
- “KYS” or credible threats (hard block)

**Gray — Gate or operator**

- Savage but substantive critique (may pass after recast)
- Satire that sounds like a personal attack on another **member** (report; operator decides)
- Multiple links in a technical post (usually OK if not an ad)

---

## Appendix A — Mapping to code (operator)

| Policy area | Implementation (current) |
|-------------|---------------------------|
| Hub naming | `assert_hub_policy` / `hubPolicyViolation` |
| Hard blocks & banned wording | `assert_content_policy`, `hard_block_violation` |
| Gate | `evaluate_opening_post`, `evaluate_reply` in `gate.py` |
| Reports | `POST …/report`, `POST /feedback`, operator routes |
| Moderation | operator page: subpop delete, user bar/timeout/pardon |

Promotional and meme rules are **policy-first** until explicit heuristics or Gate prompts are added.

---

*ProPopuli: public handles, public threads, recast before you publish.*
