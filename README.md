# TicketDesk

[![CI](https://github.com/Priyanshukainwal0/ticketdesk/actions/workflows/ci.yml/badge.svg)](https://github.com/Priyanshukainwal0/ticketdesk/actions/workflows/ci.yml)

A lightweight help-desk ticketing system built as a **Cloud / DevOps portfolio centrepiece**.  
Real app · real deployment target · real CI pipeline.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                     Client Browser                   │
│          Single-page HTML/CSS/JS console             │
└────────────────────┬────────────────────────────────┘
                     │  HTTP
┌────────────────────▼────────────────────────────────┐
│              FastAPI (uvicorn)  :8000                │
│                                                      │
│  GET  /health          →  liveness probe             │
│  GET  /                →  web console (HTML)         │
│  POST /api/tickets     →  create ticket              │
│  GET  /api/tickets     →  list (+ status filter)     │
│  GET  /api/tickets/{id}→  get one                    │
│  PATCH /api/tickets/{id}→ update                     │
│  DELETE /api/tickets/{id}→ delete                    │
│                                                      │
│  GET  /docs            →  Swagger UI (auto-gen)      │
└────────────────────┬────────────────────────────────┘
                     │  sqlite3 (swappable → PostgreSQL)
┌────────────────────▼────────────────────────────────┐
│           SQLite  (DB_PATH env var)                  │
│    Local dev  →  ticketdesk.db (cwd)                 │
│    Docker     →  /data/ticketdesk.db (named volume)  │
└─────────────────────────────────────────────────────┘
```

---

## Quick Start

### Option A — Docker (recommended)

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/ticketdesk.git
cd ticketdesk

# Build and start (DB persists in a Docker named volume)
docker compose up --build

# Open the web console
open http://localhost:8000

# Interactive API docs
open http://localhost:8000/docs
```

### Option B — Local Python

```bash
git clone https://github.com/YOUR_USERNAME/ticketdesk.git
cd ticketdesk

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

# DB_PATH defaults to ticketdesk.db in the current directory
uvicorn app.main:app --reload

open http://localhost:8000
```

---

## Running Tests

```bash
# With the venv activated:
pytest tests/ -v

# One-liner (no venv needed if deps are installed globally):
python -m pytest tests/ -v
```

Each test gets its own isolated SQLite file via a `tmp_path` fixture —  
no shared state, no teardown required.

---

## API Reference

| Method   | Path                    | Description                              | Success |
|----------|-------------------------|------------------------------------------|---------|
| `GET`    | `/health`               | Liveness probe → `{"status":"ok"}`       | 200     |
| `POST`   | `/api/tickets`          | Create a ticket (status=open)            | 201     |
| `GET`    | `/api/tickets`          | List tickets, newest-first               | 200     |
| `GET`    | `/api/tickets?status=X` | List filtered by status                  | 200     |
| `GET`    | `/api/tickets/{id}`     | Fetch one ticket                         | 200/404 |
| `PATCH`  | `/api/tickets/{id}`     | Update status / priority / assignee      | 200/404 |
| `DELETE` | `/api/tickets/{id}`     | Delete ticket                            | 204/404 |

**Ticket fields**

| Field         | Type                                      | Notes                        |
|---------------|-------------------------------------------|------------------------------|
| `id`          | integer                                   | Auto-assigned                |
| `title`       | string (1–200 chars)                      | Required                     |
| `description` | string (max 4000)                         | Optional                     |
| `requester`   | string (1–100 chars)                      | Required                     |
| `assignee`    | string \| null                            | Optional                     |
| `priority`    | `low` \| `medium` \| `high` \| `urgent`   | Default: `medium`            |
| `status`      | `open` \| `in_progress` \| `resolved` \| `closed` | Default: `open`    |
| `created_at`  | ISO-8601 datetime                         | Set on create                |
| `updated_at`  | ISO-8601 datetime                         | Updated on every PATCH       |

---

## Tech Choices

| Layer        | Choice               | Why                                                          |
|--------------|----------------------|--------------------------------------------------------------|
| Language     | Python 3.12          | Dominant in DevOps / cloud tooling; clean async story        |
| Framework    | FastAPI              | Auto Swagger docs; Pydantic validation; async-ready          |
| Validation   | Pydantic v2          | Strict typing, fast, first-class FastAPI integration         |
| Database     | SQLite + env DB_PATH | Zero-dependency for dev/demo; same code runs on PostgreSQL   |
| Server       | Uvicorn              | ASGI, production-grade, used by FastAPI officially           |
| Tests        | pytest + httpx       | Industry standard; `TestClient` hits real endpoints          |
| Container    | Docker (slim)        | Reproducible, portable, cloud-ready                          |
| Orchestration| docker-compose       | One-command local stack with persistent volume               |
| CI           | GitHub Actions       | Free for public repos; native Docker build support           |

---

## Roadmap

- [x] **Phase 1** — Containerised REST API + web console + pytest suite
- [x] **Phase 2** — GitHub Actions CI (test → Docker build)
- [x] **Phase 3** — Deployed live → https://ticketdesk-f0l0.onrender.com
- [x] **Phase 4** — Terraform IaC (AWS EC2 + security group — code ready in `terraform/`)
- [x] **Phase 5** — Monitoring: `/metrics` (Prometheus) + Grafana stack (`docker-compose.monitoring.yml`)
- [x] **Phase 6** — PostgreSQL via SQLAlchemy (single env-var swap, SQLite kept for tests)

---

## Project Structure

```
ticketdesk/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, all endpoints
│   ├── models.py        # Pydantic request/response schemas
│   ├── database.py      # SQLite helpers, connection management
│   └── static/
│       └── index.html   # Single-page web console
├── tests/
│   ├── __init__.py
│   └── test_api.py      # Full pytest suite (isolated per-test DBs)
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions: test → docker build
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

---

*Built by Priyanshu Kainwal — [LinkedIn](https://www.linkedin.com/in/priyanshu-kainwal) · [GitHub](https://github.com/Priyanshukainwal0) · [priyanshuror00@gmail.com](mailto:priyanshuror00@gmail.com)*
