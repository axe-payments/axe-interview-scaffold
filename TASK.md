# The Task

## Start here

Boot the app (see `README.md`), then open the **interactive API docs at
<http://localhost:8000/docs>** (or <http://localhost:8000/redoc> for a reading view).
That's the best single map of what's available — it lists, documents, and lets you *try*
every endpoint.

## The scenario

Emails arrive about deliveries. When one comes in, we want to **automatically call the
right person and tell them what's going on** — using the details from our CRM, spoken by
an AI phone agent.

Right now the email arrives and... nothing happens. Your job is to build the engine that
connects the two.

## What you're given

The two ends of the pipe are already built and working:

1. **An inbound email endpoint** — `POST /inbound/email/`. When an email is received it
   calls `run_workflow(email)` in `app/engine.py`, passing you an object with `from_`,
   `subject`, and `body`. (Simulate an incoming email with `./scripts/send_test_email.sh`.)

2. **An outbound call function** — `make_call(target_number=..., variables={...})` in
   `app/vapi.py`. Call it and a real phone rings; the AI agent answers using the
   `variables` you pass.

## What to build

Implement `run_workflow()` in `app/engine.py`.

## Out of scope

- Don't worry about the Vapi internals; `make_call` is a black box you just call.

## Definition of done

Running `./scripts/send_test_email.sh` makes a phone call.
