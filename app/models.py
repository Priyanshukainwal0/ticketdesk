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


# ---------------------------------------------------------------------------
# Response schema (what the API returns)
# ---------------------------------------------------------------------------

class TicketOut(BaseModel):
    """Full ticket representation returned by every read endpoint."""
    id:          int
    title:       str
    description: str
    requester:   str
    assignee:    Optional[str]
    priority:    Priority
    status:      Status
    created_at:  datetime
    updated_at:  datetime

    model_config = {"from_attributes": True}
