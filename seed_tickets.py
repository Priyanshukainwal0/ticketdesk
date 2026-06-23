"""Seed 18 realistic tickets via the REST API. Works against any deployment."""
import sys
import urllib.request
import urllib.error
import json

BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"

tickets = [
    {
        "title": "Login page returns 500 after password reset",
        "description": "Users who reset their password via the email link are getting a 500 Internal Server Error when they try to log back in. Happens on Chrome and Firefox. Reset link itself works fine.",
        "requester": "sarah.jones@company.com",
        "assignee": "priyanshu.k",
        "priority": "urgent",
        "target_status": "resolved",
    },
    {
        "title": "CI pipeline fails on feature branches with missing env vars",
        "description": "GitHub Actions build fails on any branch that isn't main. The DATABASE_URL env var is not being injected into branch builds. Need to add branch-level secrets or use a test DB override.",
        "requester": "dev.team@company.com",
        "assignee": "priyanshu.k",
        "priority": "high",
        "target_status": "resolved",
    },
    {
        "title": "Dashboard charts not loading on Safari 17",
        "description": "The Grafana-embedded charts on the ops dashboard fail to render on Safari 17.x. Console shows a CSP frame-ancestors violation. Chrome works fine.",
        "requester": "ops.lead@company.com",
        "assignee": "priyanshu.k",
        "priority": "medium",
        "target_status": "resolved",
    },
    {
        "title": "Docker image size exceeds 1.2 GB — bloating registry storage",
        "description": "The api-gateway image has grown to 1.4 GB. Need to switch to python:3.12-slim base, add .dockerignore, and use multi-stage build to strip dev dependencies.",
        "requester": "devops@company.com",
        "assignee": "priyanshu.k",
        "priority": "medium",
        "target_status": "resolved",
    },
    {
        "title": "Kubernetes pods crash-looping after config map update",
        "description": "After updating the skyops-config ConfigMap with new CHECK_INTERVAL value, all monitor-worker pods went into CrashLoopBackOff. Rolling restart did not help. Root cause: env var was renamed in worker.py but not in the config map.",
        "requester": "infra@company.com",
        "assignee": "priyanshu.k",
        "priority": "urgent",
        "target_status": "resolved",
    },
    {
        "title": "Add rate limiting to POST /api/tickets endpoint",
        "description": "Currently there is no rate limiting on ticket creation. A single client can flood the database. Implement a simple per-IP rate limit of 20 requests per minute using slowapi or a middleware.",
        "requester": "security@company.com",
        "assignee": "priyanshu.k",
        "priority": "high",
        "target_status": "resolved",
    },
    {
        "title": "Prometheus metrics not scraping from api-gateway",
        "description": "The Prometheus target for api-gateway shows state=down in /targets. The /metrics endpoint returns 200 manually but the scrape job has the wrong port (8001 instead of 8000) in prometheus.yml.",
        "requester": "monitoring@company.com",
        "assignee": "priyanshu.k",
        "priority": "high",
        "target_status": "resolved",
    },
    {
        "title": "SSL certificate renewal failed on production domain",
        "description": "Let's Encrypt cert for ticketdesk.onrender.com expired. Auto-renewal cron job was disabled after last infra change. Manually renewed — need to re-enable the renewal job and add an expiry alert.",
        "requester": "ops.lead@company.com",
        "assignee": "priyanshu.k",
        "priority": "urgent",
        "target_status": "closed",
    },
    {
        "title": "Database connection pool exhausted under load test",
        "description": "Running k6 load test with 50 VUs caused SQLAlchemy to hit pool_size limit and throw QueuePool overflow errors. Need to tune pool_size and max_overflow or switch to async connection pooling.",
        "requester": "qa@company.com",
        "assignee": "priyanshu.k",
        "priority": "high",
        "target_status": "closed",
    },
    {
        "title": "Helm chart missing resource limits for web-dashboard pod",
        "description": "The web-dashboard deployment in the Helm chart does not specify CPU/memory limits. In a shared cluster this risks noisy-neighbour issues. Add limits matching the other services.",
        "requester": "devops@company.com",
        "assignee": "priyanshu.k",
        "priority": "low",
        "target_status": "closed",
    },
    {
        "title": "HPA not scaling api-gateway pods under CPU load",
        "description": "Horizontal Pod Autoscaler is configured but pods are not scaling beyond 2 replicas during load test. metrics-server may not be installed on the k3d cluster. Need to verify metrics-server deployment.",
        "requester": "infra@company.com",
        "assignee": "priyanshu.k",
        "priority": "medium",
        "target_status": "in_progress",
    },
    {
        "title": "Migrate SQLite to PostgreSQL for production readiness",
        "description": "Current local dev uses SQLite which does not support concurrent writes. Production on Render uses PostgreSQL via DATABASE_URL. Ensure all SQL queries are Postgres-compatible and run migration tests.",
        "requester": "dev.team@company.com",
        "assignee": "priyanshu.k",
        "priority": "high",
        "target_status": "in_progress",
    },
    {
        "title": "Add GitHub Actions workflow for Helm chart linting",
        "description": "The CI pipeline tests and builds Docker images but does not lint or validate the Helm chart. Add a helm lint and helm template step to the CI workflow so chart errors are caught before merge.",
        "requester": "devops@company.com",
        "assignee": "priyanshu.k",
        "priority": "medium",
        "target_status": "in_progress",
    },
    {
        "title": "Grafana dashboard for SkyOps uptime metrics",
        "description": "Set up a Grafana dashboard showing: service uptime %, average latency per service, check frequency, and alert when any service is down for more than 2 consecutive checks.",
        "requester": "monitoring@company.com",
        "assignee": "priyanshu.k",
        "priority": "medium",
        "target_status": "in_progress",
    },
    {
        "title": "Ticket search and filtering not working on mobile viewport",
        "description": "The status filter dropdown on the TicketDesk portal overlaps the ticket list on screens narrower than 480px. Need responsive fix — convert to a stacked layout on mobile.",
        "requester": "qa@company.com",
        "priority": "low",
        "target_status": "open",
    },
    {
        "title": "Add webhook notification on ticket status change",
        "description": "When a ticket moves from open to in_progress or resolved, send a POST to a configurable webhook URL with the ticket payload. This will enable Slack notifications for the ops team.",
        "requester": "ops.lead@company.com",
        "priority": "medium",
        "target_status": "open",
    },
    {
        "title": "Write runbook for SkyOps incident response",
        "description": "Document the steps for: restarting the monitor-worker, checking API gateway health, rolling back a Helm release, and escalating to on-call. Store in the repo under docs/runbook.md.",
        "requester": "infra@company.com",
        "priority": "low",
        "target_status": "open",
    },
    {
        "title": "Implement /api/tickets export to CSV endpoint",
        "description": "Support teams need to export ticket data for reporting. Add a GET /api/tickets/export endpoint that returns a CSV file with all ticket fields. Include optional status and date range query params.",
        "requester": "sarah.jones@company.com",
        "priority": "medium",
        "target_status": "open",
    },
]


def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        BASE_URL + path,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def patch(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        BASE_URL + path,
        data=body,
        headers={"Content-Type": "application/json"},
        method="PATCH",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def main():
    print(f"Seeding tickets at {BASE_URL}\n")
    ok = 0
    for t in tickets:
        target_status = t.pop("target_status")
        payload = {k: v for k, v in t.items()}

        try:
            ticket = post("/api/tickets", payload)
            ticket_id = ticket["id"]

            if target_status != "open":
                patch(f"/api/tickets/{ticket_id}", {"status": target_status})

            print(f"  [{target_status.upper():11}] #{ticket_id} {t['title'][:55]}")
            ok += 1
        except Exception as e:
            print(f"  [ERROR] {t['title'][:55]} — {e}")

    print(f"\nDone — {ok}/{len(tickets)} tickets created.")


if __name__ == "__main__":
    main()
