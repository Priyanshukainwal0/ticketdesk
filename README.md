# 🎫 TicketDesk — Help-Desk Ticketing System

[![CI](https://github.com/Priyanshukainwal0/ticketdesk/actions/workflows/ci.yml/badge.svg)](https://github.com/Priyanshukainwal0/ticketdesk/actions/workflows/ci.yml)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-46E3B7?logo=render)](https://ticketdesk-app.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)

> A **production-ready help-desk ticketing platform** built as a full DevOps portfolio project. Real app · real CI pipeline · real cloud deployment · real infrastructure-as-code. Features Terraform (AWS), Prometheus monitoring, PostgreSQL in production, and a modern dark web console.

**Live App →** https://ticketdesk-app.onrender.com  
**API Docs →** https://ticketdesk-app.onrender.com/docs  
**Monitored by →** [SkyOps](https://skyops-api-8dn9.onrender.com)

---

## ✨ Features

- 📋 **Full ticket lifecycle** — create, update, filter, close tickets with priorities and assignees
- 🎨 **Modern dark web console** — single-page UI with status badges, priority colours, real-time filtering
- 🔌 **REST API** — 7 endpoints with auto-generated Swagger/OpenAPI docs
- 🗄️ **Dual database** — SQLite for local dev, PostgreSQL (Neon) in production via one env var
- 🐳 **Docker-first** — multi-stage build, docker-compose for local, Render for cloud
- ⚙️ **CI/CD** — GitHub Actions pipeline: lint → pytest → docker build → push
- 📊 **Observability** — Prometheus `/metrics` endpoint + Grafana stack via docker-compose
- 🏗️ **Terraform IaC** — AWS EC2 deployment code ready in `terraform/`
- ✅ **Tested** — full pytest suite with isolated per-test databases

---

## 🏗️ Architecture

```
 Browser
    │
    │  HTTP
    ▼
 FastAPI  (uvicorn :8000)
    │
    ├─ GET  /                  →  Web console (dark UI)
    ├─ GET  /health            →  Liveness probe
    ├─ GET  /metrics           →  Prometheus metrics
    ├─ GET  /docs              →  Swagger UI (auto-generated)
    │
    ├─ POST   /api/tickets     →  Create ticket
    ├─ GET    /api/tickets     →  List + filter by status
    ├─ GET    /api/tickets/{id}→  Get one
    ├─ PATCH  /api/tickets/{id}→  Update status / priority / assignee
    └─ DELETE /api/tickets/{id}→  Delete ticket
         │
         ▼
  ┌──────────────────────────────┐
  │  SQLite (local dev)          │
  │  PostgreSQL/Neon (prod)      │  ← same code, one env var swap
  └──────────────────────────────┘
```

**Production deployment flow:**

```
git push → GitHub Actions CI → pytest ✓ → docker build → Render auto-deploy → Neon PostgreSQL
```

---

## 📁 Project Structure

```
ticketdesk/
│
├── app/
│   ├── main.py            # FastAPI app — all routes, startup logic, DB init
│   ├── models.py          # Pydantic schemas (TicketCreate, TicketOut, TicketUpdate)
│   ├── database.py        # SQLite/PostgreSQL helpers, connection context manager
│   └── static/
│       └── index.html     # Single-page dark web console (vanilla JS + CSS)
│
├── tests/
│   └── test_api.py        # Full pytest suite — isolated per-test SQLite DBs
│
├── terraform/             # IaC — AWS EC2 deployment
│   ├── main.tf            # Provider, EC2 instance, security group
│   ├── variables.tf       # Input variables (region, instance type, key pair)
│   ├── outputs.tf         # Public IP output
│   └── user_data.sh       # Bootstrap script — installs Docker, runs container
│
├── .github/
│   └── workflows/
│       └── ci.yml         # GitHub Actions: lint → pytest → docker build + push
│
├── Dockerfile             # Multi-stage build (builder + slim runtime)
├── docker-compose.yml     # Local dev stack with named volume for DB
├── docker-compose.monitoring.yml  # Prometheus + Grafana monitoring stack
├── prometheus.yml         # Prometheus scrape config (targets ticketdesk:8000)
├── seed_tickets.py        # Seeds 18 realistic demo tickets via API
├── render.yaml            # Render Blueprint — IaC for cloud deployment
├── requirements.txt
└── runtime.txt            # Python version pin for Render
```

---

## 🚀 Quick Start

### Option A — Docker Compose (recommended)

```bash
git clone https://github.com/Priyanshukainwal0/ticketdesk.git
cd ticketdesk

docker compose up --build

# Web console
open http://localhost:8000

# Swagger API docs
open http://localhost:8000/docs
```

### Option B — Local Python

```bash
git clone https://github.com/Priyanshukainwal0/ticketdesk.git
cd ticketdesk

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
uvicorn app.main:app --reload

open http://localhost:8000
```

### Option C — With Monitoring Stack (Prometheus + Grafana)

```bash
# Start app + Prometheus + Grafana together
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up --build

open http://localhost:3000   # Grafana  (admin / admin)
open http://localhost:9090   # Prometheus
open http://localhost:8000   # TicketDesk
```

### Option D — Seed Demo Tickets

```bash
# Seeds 18 realistic tickets (open, in_progress, resolved, closed)
python seed_tickets.py http://localhost:8000

# Or against the live app
python seed_tickets.py https://ticketdesk-app.onrender.com
```

---

## ⚙️ CI/CD Pipeline

Every push to `main` triggers this GitHub Actions workflow:

```
push to main
    │
    ├─ Checkout code
    ├─ Set up Python 3.12
    ├─ pip install -r requirements.txt
    ├─ flake8 lint check
    ├─ pytest tests/ -v          ← isolated per-test SQLite DBs
    ├─ docker build (multi-stage)
    ├─ docker push → Docker Hub
    └─ Render auto-deploys on git push
```

Workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

---

## 🏗️ Terraform — AWS Deployment (IaC)

The `terraform/` directory contains ready-to-use infrastructure code to deploy TicketDesk on AWS EC2.

```bash
cd terraform

# Initialise providers
terraform init

# Preview what will be created
terraform plan

# Deploy (creates EC2 + security group)
terraform apply

# Outputs the public IP
terraform output public_ip
```

**What it provisions:**
- EC2 `t2.micro` instance (Free Tier eligible)
- Security group: port 22 (SSH) + port 8000 (app)
- `user_data.sh` bootstrap: installs Docker, pulls image, starts container

---

## 📊 Observability

**Prometheus metrics** are exposed at `/metrics` (via `prometheus-fastapi-instrumentator`).

**Available metrics:**
- `http_requests_total` — request count by method, handler, status
- `http_request_duration_seconds` — latency histogram
- `http_requests_in_progress` — concurrent requests gauge

**Grafana dashboard** (via `docker-compose.monitoring.yml`):
- Request rate per endpoint
- P95 / P99 latency
- Error rate (4xx / 5xx)
- Requests in flight

---

## 🔌 API Reference

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| `GET` | `/` | Web console (HTML) | 200 |
| `GET` | `/health` | Liveness probe | 200 |
| `GET` | `/metrics` | Prometheus metrics | 200 |
| `GET` | `/docs` | Swagger UI | 200 |
| `POST` | `/api/tickets` | Create a ticket | 201 |
| `GET` | `/api/tickets` | List all tickets (newest first) | 200 |
| `GET` | `/api/tickets?status=open` | Filter by status | 200 |
| `GET` | `/api/tickets/{id}` | Get one ticket | 200 / 404 |
| `PATCH` | `/api/tickets/{id}` | Update status / priority / assignee | 200 / 404 |
| `DELETE` | `/api/tickets/{id}` | Delete ticket | 204 / 404 |

### Ticket Schema

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | Auto-assigned |
| `title` | string (1–200) | Required |
| `description` | string (max 4000) | Optional |
| `requester` | string (1–100) | Required |
| `assignee` | string \| null | Optional |
| `priority` | `low` \| `medium` \| `high` \| `urgent` | Default: `medium` |
| `status` | `open` \| `in_progress` \| `resolved` \| `closed` | Default: `open` |
| `created_at` | ISO-8601 | Set on create |
| `updated_at` | ISO-8601 | Updated on every PATCH |

---

## 🛠️ Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| Language | Python 3.12 | Core language |
| Framework | FastAPI | REST API + auto docs |
| Validation | Pydantic v2 | Request/response schemas |
| Server | Uvicorn | ASGI production server |
| Database | SQLite / PostgreSQL (Neon) | Dev / production DB |
| ORM | Raw SQL (psycopg2 + sqlite3) | Lightweight, no ORM overhead |
| Containerisation | Docker | Multi-stage build |
| Orchestration | Docker Compose | Local dev stack |
| CI/CD | GitHub Actions | Lint → test → build → push |
| Metrics | Prometheus + FastAPI Instrumentator | Observability |
| Dashboards | Grafana | Metrics visualisation |
| IaC (Cloud) | Terraform | AWS EC2 provisioning |
| IaC (PaaS) | render.yaml Blueprint | Render deployment |
| Cloud | Render | Live hosting |
| DB (Cloud) | Neon PostgreSQL | Free, persistent, serverless |
| Testing | pytest + httpx | Isolated API tests |
| Frontend | Vanilla JS / CSS | Zero-dependency dark UI |

---

## 🧪 Running Tests

```bash
cd ticketdesk
pip install -r requirements.txt
pytest tests/ -v
```

Each test gets its own isolated SQLite file via a `tmp_path` fixture — no shared state, no teardown needed.

---

## 🌱 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | *(empty)* | PostgreSQL URL — if set, uses Postgres instead of SQLite |
| `DB_PATH` | `ticketdesk.db` | SQLite file path (local dev only) |
| `PORT` | `8000` | Server port (set automatically by Render) |

---

## 📦 Demo Data

18 realistic tickets are included via `seed_tickets.py`:

| Status | Count |
|--------|-------|
| `open` | 4 |
| `in_progress` | 4 |
| `resolved` | 7 |
| `closed` | 3 |

Covers priorities: `low`, `medium`, `high`, `urgent` — realistic mix for demos.

---

## 🗺️ What Was Built (All Phases)

| Phase | What Was Done |
|-------|---------------|
| **1 — API + UI** | FastAPI REST API, dark web console, SQLite, full pytest suite |
| **2 — CI/CD** | GitHub Actions: lint → pytest → docker build → Docker Hub push |
| **3 — Live Deploy** | Render deployment, Neon PostgreSQL, render.yaml Blueprint |
| **4 — Terraform** | AWS EC2 IaC — EC2 instance, security group, user_data bootstrap |
| **5 — Monitoring** | Prometheus `/metrics` + Grafana stack via docker-compose |
| **6 — PostgreSQL** | Dual-DB support (SQLite dev / PostgreSQL prod) via single env var |

---

## 👤 Author

**Priyanshu Kainwal**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-ticketdesk--app.onrender.com-46E3B7)](https://ticketdesk-app.onrender.com)
[![SkyOps](https://img.shields.io/badge/Also%20see-SkyOps%20DevOps%20Platform-3b82f6)](https://skyops-api-8dn9.onrender.com)
[![GitHub](https://img.shields.io/badge/GitHub-Priyanshukainwal0-181717?logo=github)](https://github.com/Priyanshukainwal0)
