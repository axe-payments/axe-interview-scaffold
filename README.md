# Axe Interview Scaffold

A tiny service that receives an email and (once you build the middle) places a phone
call about it. Your challenge is in **[TASK.md](./TASK.md)** — read that next.

This README is just about getting it running. It should take about 5 minutes.

## Prerequisites

- **Docker Desktop** (running). That's the only thing you need to install.
- **A phone** you can receive a call on.

That's it — no Python, Postgres, or anything else installed on your machine.

## Setup

```bash
# 1. Create your env file and paste in the keys you were given.
cp .env.example .env
#    Set VAPI_API_KEY (required). Optionally set NGROK_AUTHTOKEN to have call
#    transcripts streamed back into your logs — see "Reading the call transcript" below.

# 2. Boot everything (app + database). First run builds the image (~1-2 min).
docker compose up
```

When you see uvicorn report `Application startup complete`, it's ready. The API is at
`http://localhost:8000` (interactive docs at `http://localhost:8000/docs`).

## Confirm it works (before you build anything)

**Health check:**

```bash
curl localhost:8000/health
# {"status":"ok"}
```

**Place a real call** — confirms your Vapi credentials are good. Your phone should ring:

```bash
./scripts/test_call.sh
# enter the phone number to call when prompted (E.164, e.g. +14155551234)
```

**Look up an order** in the mock CRM:

```bash
curl localhost:8000/mock-crm/orders/ORD-12345/
```

### Reading the call transcript

If you set `NGROK_AUTHTOKEN` in `.env`, `docker compose up` also starts an **ngrok** tunnel
(no setup needed — it comes up with everything else). The app discovers its public URL and
asks Vapi to POST the transcript back when a call ends; it's then **pretty-printed in the
`docker compose up` logs**, so you can read a call instead of staying on the line. Without the
token, calls still work — you just won't see the transcript. (The tunnel's inspector is at
<http://localhost:4040>.)

**See what's wired up** — the agents (and the `{{ variables }}` each expects) and the
phone numbers you can call from. The best view is the docs at `http://localhost:8000/docs`,
or from the terminal:

```bash
curl localhost:8000/agents/
curl localhost:8000/phone-numbers/
```

**Send a test email** — this hits the inbound endpoint. Out of the box the engine just
logs it (your job is to make it do more):

```bash
./scripts/send_test_email.sh
# enter From / To / Subject / Body when prompted
```

Watch the `docker compose up` terminal — you'll see the email arrive and `run_workflow`
log it.

## Your dev loop

The source is mounted into the container with hot-reload, so **just edit files and save** —
the app restarts automatically. The file you'll spend your time in is
**`app/engine.py`**. Re-run `./scripts/send_test_email.sh` to test each change.

## Editor setup (optional)

The app runs in Docker, so your editor's Python tooling (import resolution, auto-import,
lint) needs the packages too. Pick whichever you prefer — both are optional:

- **Dev container (no local Python):** in Cursor/VSCode run **"Dev Containers: Reopen in
  Container"**. You're now editing inside the app container, so the interpreter already has
  every dependency. (Config in `.devcontainer/`.)
- **Local venv:** run **`./scripts/setup_venv.sh`** (needs Python 3.12), then pick
  `./.venv/bin/python` via "Python: Select Interpreter". The `.vscode/` settings already
  default to it and enable auto-import + [ruff](https://docs.astral.sh/ruff/) formatting.

## How the pieces fit

| File | What it is |
|------|------------|
| `app/inbound.py` | **Given.** `POST /inbound/email/` — receives the email, hands it to `run_workflow()`. |
| `app/vapi.py` | **Given.** `make_call(target_number=..., variables={...})` — places a call. |
| `app/mock_crm.py` | **Given.** `GET /mock-crm/orders/` and `/{id}/` — fake "look up the order" API. |
| `app/catalog.py` | **Given.** `GET /agents/` and `GET /phone-numbers/` — discover what's wired up. |
| `app/webhooks.py` | **Given.** `POST /webhooks/vapi/` — receives the end-of-call transcript and logs it. |
| `app/engine.py` | **Yours.** `run_workflow(email)` — the engine you build. |
| `app/models.py` | Optional. Add Tortoise models here; tables auto-create on restart. |
| `app/config.py` / `app/main.py` | Config + app wiring. You shouldn't need to touch these. |

## Inspecting the database

A database browser (Adminer) runs at **`http://localhost:8080`**.
Log in with — System: `PostgreSQL`, Server: `postgres`, Username/Password: `postgres`,
Database: `interview`.

## Useful commands

```bash
docker compose up            # start (foreground, shows logs)
docker compose up -d         # start in the background
docker compose logs -f app   # follow just the app logs
docker compose down          # stop
docker compose down -v       # stop and wipe the database
```
