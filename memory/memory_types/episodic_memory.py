from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from memory.memory_types.base_memory import BaseMemory


# ==========================================================
# Event Type
# ==========================================================

class EpisodeType(str, Enum):
    SEARCH = "search"
    PURCHASE = "purchase"
    CLICK = "click"
    VIEW = "view"
    CART = "cart"
    RATING = "rating"
    FEEDBACK = "feedback"
    RECOMMENDATION = "recommendation"


# ==========================================================
# Episode
# ==========================================================

@dataclass(slots=True)
class Episode:

    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: EpisodeType = EpisodeType.SEARCH
    timestamp: datetime = field(default_factory=datetime.utcnow)

    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


# ==========================================================
# Episodic Memory
# ==========================================================

@dataclass(slots=True)
class EpisodicMemory(BaseMemory):

    event: Episode = field(default_factory=Episode)

    importance: float = 0.5
    confidence: float = 1.0

    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)

    archived: bool = False
    tags: list[str] = field(default_factory=list)

    # -----------------------------------------------------

    @property
    def event_type(self):
        return self.event.event_type

    @property
    def timestamp(self):
        return self.event.timestamp

    @property
    def payload(self):
        return self.event.payload

    @property
    def metadata(self):
        return self.event.metadata

    # =====================================================
    # Factory Methods
    # =====================================================

    @classmethod
    def search(
        cls,
        customer_id: str,
        query: str,
        filters: dict | None = None,
    ):

        payload = {
            "query": query,
        }

        if filters:
            payload.update(filters)

        return cls(

            customer_id=customer_id,

            event=Episode(

                event_type=EpisodeType.SEARCH,

                payload=payload,

            ),

        )

    @classmethod
    def purchase(
        cls,
        customer_id: str,
        product_id: str,
        quantity: int = 1,
        payload: dict | None = None,
    ):
        return cls(
            customer_id=customer_id,
            event=Episode(
                event_type=EpisodeType.PURCHASE,
                payload=payload or {
                    "product_id": product_id,
                    "quantity": quantity,
                },
            ),
            importance=1.0,
        )

    @classmethod
    def click(
        cls,
        customer_id: str,
        product_id: str,
    ):
        return cls(
            customer_id=customer_id,
            event=Episode(
                event_type=EpisodeType.CLICK,
                payload={
                    "product_id": product_id,
                },
            ),
        )

    @classmethod
    def view(
        cls,
        customer_id: str,
        product_id: str,
    ):
        return cls(
            customer_id=customer_id,
            event=Episode(
                event_type=EpisodeType.VIEW,
                payload={
                    "product_id": product_id,
                },
            ),
        )

    @classmethod
    def cart(
        cls,
        customer_id: str,
        product_id: str,
        quantity: int = 1,
    ):
        return cls(
            customer_id=customer_id,
            event=Episode(
                event_type=EpisodeType.CART,
                payload={
                    "product_id": product_id,
                    "quantity": quantity,
                },
            ),
        )

    @classmethod
    def rating(
        cls,
        customer_id: str,
        product_id: str,
        rating: float,
    ):
        return cls(
            customer_id=customer_id,
            event=Episode(
                event_type=EpisodeType.RATING,
                payload={
                    "product_id": product_id,
                    "rating": rating,
                },
            ),
        )

    @classmethod
    def feedback(
        cls,
        customer_id: str,
        text: str,
        sentiment: str | None = None,
    ):
        return cls(
            customer_id=customer_id,
            event=Episode(
                event_type=EpisodeType.FEEDBACK,
                payload={
                    "text": text,
                },
                metadata={
                    "sentiment": sentiment,
                },
            ),
        )

    @classmethod
    def recommendation(
        cls,
        customer_id: str,
        recommendation_id: str,
        accepted: bool = False,
    ):
        return cls(
            customer_id=customer_id,
            event=Episode(
                event_type=EpisodeType.RECOMMENDATION,
                payload={
                    "recommendation_id": recommendation_id,
                    "accepted": accepted,
                },
            ),
        )

    # =====================================================

    def accessed(self):

        self.access_count += 1
        self.last_accessed = datetime.utcnow()

    def archive(self):

        self.archived = True

    def restore(self):

        self.archived = False

    def add_tag(self, tag: str):

        tag = tag.strip().lower()

        if tag and tag not in self.tags:
            self.tags.append(tag)
    
    print("USING NEW TO_DICT")

    def to_dict(self):

        return {

            "customer_id": self.customer_id,

            "event_id": self.event.event_id,

            "event_type": self.event.event_type.value,

            "timestamp": self.event.timestamp.isoformat(),

            "payload": self.event.payload,

            "metadata": self.event.metadata,

            "importance": self.importance,

            "confidence": self.confidence,

            "access_count": self.access_count,

            "archived": self.archived,

            "tags": self.tags,

        }


__all__ = [
    "EpisodeType",
    "Episode",
    "EpisodicMemory",
]