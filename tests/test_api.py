"""
pytest suite for the TicketDesk API.

Each test gets its own fresh SQLite DB via the `client` fixture, which sets
DB_PATH before entering the TestClient context (triggering lifespan/init_db).
"""

import os
import time

import pytest
from fastapi.testclient import TestClient

from app.main import app


# ---------------------------------------------------------------------------
# Fixture — isolated DB per test
# ---------------------------------------------------------------------------

@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    Yield a TestClient backed by a brand-new SQLite file.
    monkeypatch.setenv restores the env var automatically after the test.
    """
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make(client, **overrides) -> dict:
    """POST a ticket with sensible defaults; assert 201 and return JSON."""
    payload = {
        "title":       "Printer not working",
        "description": "Jams every time.",
        "requester":   "alice@example.com",
        "assignee":    "bob@example.com",
        "priority":    "high",
        **overrides,
    }
    res = client.post("/api/tickets", json=payload)
    assert res.status_code == 201, res.text
    return res.json()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def test_create_returns_full_object(client):
    data = _make(client)
    assert data["id"] == 1
    assert data["title"] == "Printer not working"
    assert data["status"] == "open"        # always starts open
    assert data["priority"] == "high"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_defaults_priority_medium(client):
    res = client.post("/api/tickets", json={
        "title": "No priority", "requester": "u@example.com"
    })
    assert res.status_code == 201
    assert res.json()["priority"] == "medium"


def test_create_null_assignee(client):
    res = client.post("/api/tickets", json={
        "title": "No assignee", "requester": "u@example.com"
    })
    assert res.status_code == 201
    assert res.json()["assignee"] is None


# ---------------------------------------------------------------------------
# Validation errors (422)
# ---------------------------------------------------------------------------

def test_create_missing_title_422(client):
    res = client.post("/api/tickets", json={"requester": "alice@example.com"})
    assert res.status_code == 422


def test_create_missing_requester_422(client):
    res = client.post("/api/tickets", json={"title": "Something broke"})
    assert res.status_code == 422


def test_create_invalid_priority_422(client):
    res = client.post("/api/tickets", json={
        "title": "T", "requester": "u@example.com", "priority": "critical"
    })
    assert res.status_code == 422


def test_create_empty_title_422(client):
    res = client.post("/api/tickets", json={"title": "", "requester": "u@example.com"})
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# Get one
# ---------------------------------------------------------------------------

def test_get_returns_correct_data(client):
    created = _make(client)
    res = client.get(f"/api/tickets/{created['id']}")
    assert res.status_code == 200
    assert res.json() == created


def test_get_nonexistent_404(client):
    assert client.get("/api/tickets/9999").status_code == 404


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

def test_list_all(client):
    _make(client, title="First")
    _make(client, title="Second")
    data = client.get("/api/tickets").json()
    assert len(data) == 2
    assert data[0]["title"] == "Second"   # newest first
    assert data[1]["title"] == "First"


def test_list_status_filter(client):
    _make(client, title="Stay open")
    _make(client, title="Gets resolved")
    client.patch("/api/tickets/2", json={"status": "resolved"})

    open_list     = client.get("/api/tickets?status=open").json()
    resolved_list = client.get("/api/tickets?status=resolved").json()

    assert len(open_list) == 1 and open_list[0]["title"] == "Stay open"
    assert len(resolved_list) == 1 and resolved_list[0]["title"] == "Gets resolved"


def test_list_empty(client):
    assert client.get("/api/tickets").json() == []


def test_list_invalid_status_422(client):
    assert client.get("/api/tickets?status=nonexistent").status_code == 422


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def test_update_status(client):
    t = _make(client)
    res = client.patch(f"/api/tickets/{t['id']}", json={"status": "in_progress"})
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"


def test_update_priority(client):
    t = _make(client)
    res = client.patch(f"/api/tickets/{t['id']}", json={"priority": "urgent"})
    assert res.status_code == 200
    assert res.json()["priority"] == "urgent"


def test_update_assignee(client):
    t = _make(client)
    res = client.patch(f"/api/tickets/{t['id']}", json={"assignee": "carol@example.com"})
    assert res.status_code == 200
    assert res.json()["assignee"] == "carol@example.com"


def test_update_bumps_updated_at(client):
    t = _make(client)
    original = t["updated_at"]
    time.sleep(0.01)
    patched = client.patch(f"/api/tickets/{t['id']}", json={"status": "resolved"}).json()
    assert patched["updated_at"] != original


def test_update_nonexistent_404(client):
    assert client.patch("/api/tickets/9999", json={"status": "closed"}).status_code == 404


def test_update_empty_body_422(client):
    t = _make(client)
    assert client.patch(f"/api/tickets/{t['id']}", json={}).status_code == 422


def test_update_invalid_status_422(client):
    t = _make(client)
    assert client.patch(f"/api/tickets/{t['id']}", json={"status": "broken"}).status_code == 422


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def test_delete(client):
    t = _make(client)
    assert client.delete(f"/api/tickets/{t['id']}").status_code == 204
    assert client.get(f"/api/tickets/{t['id']}").status_code == 404


def test_delete_nonexistent_404(client):
    assert client.delete("/api/tickets/9999").status_code == 404
