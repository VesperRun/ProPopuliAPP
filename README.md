# ProPopuli

Popular-forum layout (hubs, posts, threads) with a **Reframing Gate** on replies. Persistent public handles (no legal names). AI is optional: classification + challenge only when `OPENAI_API_KEY` is set; otherwise heuristics run locally.

## Prerequisites

- Node.js 18+
- Python 3.10+ (3.14 supported; pinned `pydantic` must match a wheel for your Python version)

## Setup

From the repo root:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
cd ../frontend
npm install
```

Copy env templates: `backend/.env.example` → `backend/.env`; optional `frontend/.env.example` → `frontend/.env.local`.

**Secrets:** `OPENAI_API_KEY` and `SECRET_KEY` live in **backend** env / host secrets only. The Next app never calls OpenAI and must not define `OPENAI_*` or `NEXT_PUBLIC_*` OpenAI vars. Without a backend key, the Gate uses local heuristics.

Optional: set `OPENAI_API_KEY` in `backend/.env` (or deploy secrets) for classifier + challenge on replies.

## Run

Terminal 1 (backend):

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

Terminal 2 (frontend):

```bash
cd frontend
npm run dev
```

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Health: http://localhost:8000/health

## MVP flow

1. Register → pick a handle
2. Open **h/general** or **h/build**
3. Create a post
4. Reply on the thread — teardown language gets **422** with a rewrite challenge; constructive replies publish

## Structure

- `backend/` — FastAPI, SQLite, JWT auth, Gate on `POST /posts/{id}/comments`
- `frontend/` — Next.js 14, light UI
