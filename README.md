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
# 1. Create your env file and fill in the values you were given.
cp .env.example .env
#    Open .env and paste in the Vapi credentials, and set DEMO_TARGET_PHONE to YOUR phone.

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
# enter your phone number when prompted (E.164, e.g. +14155551234)
```

**Look up an order** in the mock CRM:

```bash
curl localhost:8000/mock-crm/orders/ORD-12345/
```

**Send a test email** — this hits the inbound endpoint. Out of the box the engine just
logs it (your job is to make it do more):

```bash
./scripts/send_test_email.sh
# enter From / Subject / Body when prompted
```

Watch the `docker compose up` terminal — you'll see the email arrive and `run_workflow`
log its "TODO" line.

## Your dev loop

The source is mounted into the container with hot-reload, so **just edit files and save** —
the app restarts automatically. The file you'll spend your time in is
**`app/engine.py`**. Re-run `./scripts/send_test_email.sh` to test each change.

## How the pieces fit

| File | What it is |
|------|------------|
| `app/inbound.py` | **Given.** `POST /inbound/email/` — receives the email, hands it to `run_workflow()`. |
| `app/vapi.py` | **Given.** `make_call(target_number=..., variables={...})` — places a call. |
| `app/mock_crm.py` | **Given.** `GET /mock-crm/orders/{id}/` — fake "look up the order" API. |
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
