# Support Ticket API


This project contains **a number of hidden bugs**. Your task is to **debug and fix them**. The goal is to solve as many as you can—it’s okay if you don’t find all of them.

**Reference:** The correct API behaviour is defined in [api-specifications.md](api-specifications.md). Use it as the source of truth.

**Workflow:** Fork this repository and do all your work (and commits) in your fork.

**Code quality:** Read and understand the existing code and your own changes. Don’t apply fixes without understanding what the code does and why you’re changing it.

**AI tools:** You may use AI tools. If you do, you **must share the relevant chat history with us during the interview**.

### Mandatory for the interview

- Bring your laptop.
- Ensure the project is set up on your machine before you come.
- If you used AI, have the chat history ready to share.

---

FastAPI-based REST API for a support ticket triage system. See [api-specifications.md](api-specifications.md) for full specifications.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Configuration

Set environment variables (optional; defaults shown):

- `MAX_QUEUES` – maximum number of queues (default: `10`)
- `MAX_TICKETS_PER_QUEUE` – optional per-queue ticket limit
- `DATABASE_URL` – database URL (default: `sqlite:///./support.db`)

Example:

```bash
export MAX_QUEUES=20
```

## Run

```bash
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs

## Endpoints

- `POST /queues` – create queue
- `GET /queues` – list queues
- `GET /queues/full-view` – queues with nested tickets
- `DELETE /queues/{queue_id}` – remove queue
- `POST /queues/{queue_id}/tickets` – add ticket batch to queue
- `POST /queues/{queue_id}/tickets/bulk` – bulk add tickets
- `GET /queues/{queue_id}/tickets` – list tickets in queue
- `POST /tickets` – create standalone ticket
- `GET /tickets/{ticket_id}` – get single ticket
- `PATCH /tickets/{ticket_id}/complexity` – update ticket complexity
- `DELETE /queues/{queue_id}/tickets/{ticket_id}` – remove ticket or quantity
- `DELETE /queues/{queue_id}/tickets` – clear queue or remove specific tickets
- `POST /resolve` – resolve a ticket batch
- `GET /resolve/overtime-breakdown?overtime=<amount>` – breakdown overtime into standard effort blocks
- `GET /health` – health check
