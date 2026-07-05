"""
memory_core/models.py

Shared models used across the memory subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


# ==========================================================
# Event Types
# ==========================================================

class EventType(str, Enum):
    SEARCH = "search"
    PURCHASE = "purchase"
    FEEDBACK = "feedback"
    RATING = "rating"


# ==========================================================
# Memory Event
# ==========================================================

@dataclass(slots=True)
class MemoryEvent:
    """
    Raw event received by MemoryService.
    """

    event_id: str = field(default_factory=lambda: str(uuid4()))

    customer_id: str = ""

    event_type: EventType = EventType.SEARCH

    payload: dict[str, Any] = field(default_factory=dict)

    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:

        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):

        return cls(**data)


# ==========================================================
# Retrieval Request
# ==========================================================

@dataclass(slots=True)
class RetrievalRequest:
    """
    Request sent to MemoryRetriever.
    """

    customer_id: str

    query: str

    top_k: int = 10


# ==========================================================
# Retrieval Response
# ==========================================================

@dataclass(slots=True)
class RetrievalResponse:
    """
    Response returned by MemoryRetriever.
    """

    customer_id: str

    query: str

    memories: list[Any] = field(default_factory=list)


# ==========================================================
# Health Status
# ==========================================================

@dataclass(slots=True)
class HealthStatus:
    """
    Generic health response.
    """

    status: str = "healthy"

    message: str = ""


# ==========================================================
# Helper Functions
# ==========================================================

def create_search_event(
    customer_id: str,
    query: str,
) -> MemoryEvent:

    return MemoryEvent(

        customer_id=customer_id,

        event_type=EventType.SEARCH,

        payload={

            "query": query,

        },

    )


def create_purchase_event(
    customer_id: str,
    product_id: str,
    quantity: int = 1,
) -> MemoryEvent:

    return MemoryEvent(

        customer_id=customer_id,

        event_type=EventType.PURCHASE,

        payload={

            "product_id": product_id,

            "quantity": quantity,

        },

    )


def create_feedback_event(
    customer_id: str,
    feedback: str,
) -> MemoryEvent:

    return MemoryEvent(

        customer_id=customer_id,

        event_type=EventType.FEEDBACK,

        payload={

            "feedback": feedback,

        },

    )


def create_rating_event(
    customer_id: str,
    product_id: str,
    rating: float,
) -> MemoryEvent:

    return MemoryEvent(

        customer_id=customer_id,

        event_type=EventType.RATING,

        payload={

            "product_id": product_id,

            "rating": rating,

        },

    )


# ==========================================================
# Public Exports
# ==========================================================

__all__ = [

    "EventType",

    "MemoryEvent",

    "RetrievalRequest",

    "RetrievalResponse",

    "HealthStatus",

    "create_search_event",

    "create_purchase_event",

    "create_feedback_event",

    "create_rating_event",

]