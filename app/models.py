"""
Pydantic models for request validation and response serialisation.

Pydantic is FastAPI's data layer: it validates incoming JSON, coerces types,
and documents the schema automatically (visible at /docs).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Priority(str, Enum):
    """String enum so values are stored directly in SQLite as plain text."""
    low    = "low"
    medium = "medium"
    high   = "high"
    urgent = "urgent"


class Status(str, Enum):
    open        = "open"
    in_progress = "in_progress"
    resolved    = "resolved"
    closed      = "closed"


class Category(str, Enum):
    """
    Service-desk categories the triage model classifies into.

    Deliberately small and non-overlapping — a classifier given twenty
    similar options produces worse results than one given eight distinct
    ones. 'other' is the escape hatch, and a rising 'other' rate is a
    signal the category list needs revisiting.
    """
    hardware       = "hardware"
    software       = "software"
    network        = "network"
    account_access = "account_access"
    email          = "email"
    printing       = "printing"
    security       = "security"
    other          = "other"


# ---------------------------------------------------------------------------
# Request schemas (what the client sends)
# ---------------------------------------------------------------------------

class TicketCreate(BaseModel):
    """Payload for POST /api/tickets."""
    title:       str           = Field(..., min_length=1, max_length=200)
    description: str           = Field(default="", max_length=4000)
    requester:   str           = Field(..., min_length=1, max_length=100)
    assignee:    Optional[str] = Field(default=None, max_length=100)
    priority:    Priority      = Field(default=Priority.medium)
    # status absent — new tickets always start as 'open'


class TicketUpdate(BaseModel):
    """
    Payload for PATCH /api/tickets/{id}.
    Every field optional; send only what you want to change.
    """
    status:   Optional[Status]   = None
    priority: Optional[Priority] = None
    assignee: Optional[str]      = Field(default=None, max_length=100)


class TicketTriage(BaseModel):
    """
    Payload for PATCH /api/tickets/{id}/triage — written by the automated
    triage pipeline rather than by a human.

    `confidence` is the model's own reported certainty. It is stored rather
    than acted on here: the decision about what to do with a low-confidence
    classification belongs to the caller, not to this endpoint.
    """
    category:           Category = Field(..., description="Classified category.")
    priority:           Priority = Field(..., description="Suggested priority.")
    confidence:         float    = Field(
        ..., ge=0.0, le=1.0,
        description="Model's self-reported confidence, 0.0–1.0.",
    )
    summary:            str      = Field(
        default="", max_length=500,
        description="One-line restatement of the issue.",
    )
    suggested_response: str      = Field(
        default="", max_length=4000,
        description="Draft first reply for an agent to review and send.",
    )


# ---------------------------------------------------------------------------
# Response schema (what the API returns)
# ---------------------------------------------------------------------------

class TicketOut(BaseModel):
    """
    Full ticket representation returned by every read endpoint.

    The triage fields are all Optional and default to None: tickets created
    before the triage pipeline existed, and tickets not yet processed by it,
    are valid and must still serialise.
    """
    id:          int
    title:       str
    description: str
    requester:   str
    assignee:    Optional[str]
    priority:    Priority
    status:      Status
    created_at:  datetime
    updated_at:  datetime

    # --- populated by the AI triage pipeline -------------------------------
    category:           Optional[Category] = None
    ai_confidence:      Optional[float]    = None
    ai_summary:         Optional[str]      = None
    suggested_response: Optional[str]      = None
    triaged_at:         Optional[datetime] = None

    model_config = {"from_attributes": True}
