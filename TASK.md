# The Task

## Start here

Boot the app (see `README.md`), then open the **interactive API docs at
<http://localhost:8000/docs>** (or <http://localhost:8000/redoc> for a reading view).
That's the best single map of what's available — it lists, documents, and lets you *try*
every endpoint:

- **Email intake (entry point)** — `POST /inbound/email/`, where an email comes in.
- **Make a call (exit point)** — `POST /debug/call/`, which places a real call.
- **Discovery** — `GET /agents/` and `GET /phone-numbers/`: the AI agents and phone
  numbers wired up for you. Each agent lists the `{{ merge_variables }}` its script
  expects — that's the contract for what to pass in `make_call(variables=...)`.
- **Mock CRM** — `GET /mock-crm/orders/` (list) and `GET /mock-crm/orders/{id}/` (lookup).

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
   `variables` you pass. Each agent expects specific `{{ merge_variables }}` — check
   `GET /agents/` to see exactly which, and map the CRM fields onto them.

You also have a **mock CRM** to enrich emails with order data:
`GET /mock-crm/orders/{order_id}/` returns a contact name, phone, status, delivery
window, and address. Try `ORD-12345` and `ORD-67890` (and `ORD-ERROR` / `ORD-SLOW` if you
want to test failure handling), or `GET /mock-crm/orders/` to list them.

To see everything that's wired up — the agents (and the variables each expects) and the
phone numbers you can call from — use the discovery endpoints `GET /agents/` and
`GET /phone-numbers/`, or just browse <http://localhost:8000/docs>.

## What to build

Implement `run_workflow()` (and any supporting code/data model you design) so that an
incoming email results in a phone call:

1. Read the email and work out **which order** it's about.
2. **Look the order up** in the mock CRM to get the contact and details.
3. **Call the contact** with `make_call()`, passing the order details as `variables` so
   the agent can speak them.

**How you structure this is the interesting part, and it's up to you.** Think of it as a
small, configurable *workflow engine*: a series of steps — filter, extract, enrich, call —
that pass data from one to the next. How a workflow is defined, stored, and executed is
your design. We're interested in how you model the problem, not in a single hard-coded
`if` statement.

## Three agents are available

There are **three** pre-configured agents and **two** phone numbers (see `GET /agents/`
and `GET /phone-numbers/`). `make_call` uses the first agent + first number by default;
pass `assistant_id` / `phone_number_id` to choose another. The agents cover different
scenarios (e.g. delivery completed vs. delayed, driver vs. customer), so your engine
should **route to the right agent** based on the email — a nice way to show branching.

## Out of scope

- **No frontend.** Define workflows in code or a config file — whatever you like.
- **No auth, no deployment, no real email infra.** Everything is local.
- Don't worry about the Vapi internals; `make_call` is a black box you just call.

## Definition of done

Running `./scripts/send_test_email.sh` with an email about a real order results in a
phone call to that order's contact, and the agent speaks the order details you extracted
and enriched.

## Tips

- Get the smoke tests in the README passing first, so you know the call path works.
- The app hot-reloads on save. Iterate with `./scripts/send_test_email.sh`.
- You don't have to use the database — but it's wired up (`app/models.py`) if you want to
  persist workflows or execution history.
- Talk through your design as you go; we care about your reasoning and trade-offs.
