"""Seed 18 realistic tickets directly into the SQLite database."""
import sqlite3
from datetime import datetime, timezone, timedelta

DB = "ticketdesk.db"

tickets = [
    # (title, description, requester, assignee, priority, status, days_ago)
    (
        "Login page returns 500 after password reset",
        "Users who reset their password via the email link are getting a 500 Internal Server Error when they try to log back in. Happens on Chrome and Firefox. Reset link itself works fine.",
        "sarah.jones@company.com", "priyanshu.k", "urgent", "resolved", 12
    ),
    (
        "CI pipeline fails on feature branches with missing env vars",
        "GitHub Actions build fails on any branch that isn't main. The DATABASE_URL env var is not being injected into branch builds. Need to add branch-level secrets or use a test DB override.",
        "dev.team@company.com", "priyanshu.k", "high", "resolved", 10
    ),
    (
        "Dashboard charts not loading on Safari 17",
        "The Grafana-embedded charts on the ops dashboard fail to render on Safari 17.x. Console shows a CSP frame-ancestors violation. Chrome works fine.",
        "ops.lead@company.com", "priyanshu.k", "medium", "resolved", 9
    ),
    (
        "Docker image size exceeds 1.2 GB — bloating registry storage",
        "The api-gateway image has grown to 1.4 GB. Need to switch to python:3.12-slim base, add .dockerignore, and use multi-stage build to strip dev dependencies.",
        "devops@company.com", "priyanshu.k", "medium", "resolved", 8
    ),
    (
        "Kubernetes pods crash-looping after config map update",
        "After updating the skyops-config ConfigMap with new CHECK_INTERVAL value, all monitor-worker pods went into CrashLoopBackOff. Rolling restart did not help. Root cause: env var was renamed in worker.py but not in the config map.",
        "infra@company.com", "priyanshu.k", "urgent", "resolved", 7
    ),
    (
        "Add rate limiting to POST /api/tickets endpoint",
        "Currently there is no rate limiting on ticket creation. A single client can flood the database. Implement a simple per-IP rate limit of 20 requests per minute using slowapi or a middleware.",
        "security@company.com", "priyanshu.k", "high", "resolved", 6
    ),
    (
        "Prometheus metrics not scraping from api-gateway",
        "The Prometheus target for api-gateway shows state=down in /targets. The /metrics endpoint returns 200 manually but the scrape job has the wrong port (8001 instead of 8000) in prometheus.yml.",
        "monitoring@company.com", "priyanshu.k", "high", "resolved", 5
    ),
    (
        "SSL certificate renewal failed on production domain",
        "Let's Encrypt cert for ticketdesk.onrender.com expired. Auto-renewal cron job was disabled after last infra change. Manually renewed — need to re-enable the renewal job and add an expiry alert.",
        "ops.lead@company.com", "priyanshu.k", "urgent", "closed", 15
    ),
    (
        "Database connection pool exhausted under load test",
        "Running k6 load test with 50 VUs caused SQLAlchemy to hit pool_size limit and throw QueuePool overflow errors. Need to tune pool_size and max_overflow or switch to async connection pooling.",
        "qa@company.com", "priyanshu.k", "high", "closed", 14
    ),
    (
        "Helm chart missing resource limits for web-dashboard pod",
        "The web-dashboard deployment in the Helm chart does not specify CPU/memory limits. In a shared cluster this risks noisy-neighbour issues. Add sensible limits matching the other services.",
        "devops@company.com", "priyanshu.k", "low", "closed", 11
    ),
    (
        "HPA not scaling api-gateway pods under CPU load",
        "Horizontal Pod Autoscaler is configured but pods are not scaling beyond 2 replicas during load test. metrics-server may not be installed on the k3d cluster. Need to verify metrics-server deployment.",
        "infra@company.com", "priyanshu.k", "medium", "in_progress", 3
    ),
    (
        "Migrate SQLite to PostgreSQL for production readiness",
        "Current local dev uses SQLite which doesn't support concurrent writes. Production on Render uses PostgreSQL via DATABASE_URL. Need to ensure all SQL queries are Postgres-compatible and run migration tests.",
        "dev.team@company.com", "priyanshu.k", "high", "in_progress", 2
    ),
    (
        "Add GitHub Actions workflow for Helm chart linting",
        "The CI pipeline tests and builds Docker images but does not lint or validate the Helm chart. Add a helm lint and helm template step to the CI workflow so chart errors are caught before merge.",
        "devops@company.com", "priyanshu.k", "medium", "in_progress", 2
    ),
    (
        "Grafana dashboard for SkyOps uptime metrics",
        "Set up a Grafana dashboard showing: service uptime %, average latency per service, check frequency, and alert when any service is down for more than 2 consecutive checks.",
        "monitoring@company.com", "priyanshu.k", "medium", "in_progress", 1
    ),
    (
        "Ticket search and filtering not working on mobile viewport",
        "The status filter dropdown on the TicketDesk portal overlaps the ticket list on screens narrower than 480px. Need responsive fix — convert to a stacked layout on mobile.",
        "qa@company.com", None, "low", "open", 1
    ),
    (
        "Add webhook notification on ticket status change",
        "When a ticket moves from open to in_progress or resolved, send a POST to a configurable webhook URL with the ticket payload. This will enable Slack notifications for the ops team.",
        "ops.lead@company.com", None, "medium", "open", 0
    ),
    (
        "Write runbook for SkyOps incident response",
        "Document the steps for: restarting the monitor-worker, checking API gateway health, rolling back a Helm release, and escalating to on-call. Store in the repo under docs/runbook.md.",
        "infra@company.com", None, "low", "open", 0
    ),
    (
        "Implement /api/tickets export to CSV endpoint",
        "Support teams need to export ticket data for reporting. Add a GET /api/tickets/export endpoint that returns a CSV file with all ticket fields. Include optional status and date range query params.",
        "sarah.jones@company.com", None, "medium", "open", 0
    ),
]

def seed():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Check existing count
    existing = cur.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    print(f"Existing tickets: {existing}")

    now = datetime.now(timezone.utc)
    inserted = 0

    for title, desc, requester, assignee, priority, status, days_ago in tickets:
        created = (now - timedelta(days=days_ago)).isoformat()
        updated = created

        cur.execute("""
            INSERT INTO tickets (title, description, requester, assignee, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, desc, requester, assignee, priority, status, created, updated))
        inserted += 1
        print(f"  [{status.upper():11}] {title[:60]}")

    conn.commit()
    conn.close()
    print(f"\nDone — inserted {inserted} tickets. Total now: {existing + inserted}")

if __name__ == "__main__":
    seed()
