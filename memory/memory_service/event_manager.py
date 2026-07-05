from __future__ import annotations

from enum import Enum
from typing import Any

from memory.memory_types.episodic_memory import EpisodicMemory


# ==========================================================
# Event Types
# ==========================================================

class EventType(str, Enum):
    SEARCH = "search"
    PURCHASE = "purchase"
    CLICK = "click"
    VIEW = "view"
    CART = "cart"
    RATING = "rating"
    FEEDBACK = "feedback"
    LOGIN = "login"
    RECOMMENDATION = "recommendation"


# ==========================================================
# Event Manager
# ==========================================================

class EventManager:

    """
    Creates EpisodicMemory objects from
    incoming application events.
    """

    def create(
        self,
        event_type: EventType,
        customer_id: str,
        **kwargs: Any,
    ) -> EpisodicMemory:

        handlers = {

            EventType.SEARCH: self._search,

            EventType.PURCHASE: self._purchase,

            EventType.CLICK: self._click,

            EventType.VIEW: self._view,

            EventType.CART: self._cart,

            EventType.RATING: self._rating,

            EventType.FEEDBACK: self._feedback,

            EventType.LOGIN: self._login,

            EventType.RECOMMENDATION: self._recommendation,

        }

        handler = handlers.get(event_type)

        if handler is None:

            raise ValueError(
                f"Unsupported event: {event_type}"
            )

        return handler(customer_id, **kwargs)

    # --------------------------------------------------

    def _search(self, customer_id: str, **data):

        return EpisodicMemory.search(

            customer_id=customer_id,

            query=data["query"],

            filters=data.get("filters"),

        )

    # --------------------------------------------------

    def _purchase(self, customer_id: str, **data):

        return EpisodicMemory.purchase(

            customer_id=customer_id,

            product_id=data["product_id"],

            quantity=data.get("quantity", 1),

            payload=data,

        )

    # --------------------------------------------------

    def _click(self, customer_id: str, **data):

        return EpisodicMemory.click(

            customer_id,

            data["product_id"],

        )

    # --------------------------------------------------

    def _view(self, customer_id: str, **data):

        return EpisodicMemory.view(

            customer_id,

            data["product_id"],

        )

    # --------------------------------------------------

    def _cart(self, customer_id: str, **data):

        return EpisodicMemory.cart(

            customer_id,

            data["product_id"],

            data.get("quantity", 1),

        )

    # --------------------------------------------------

    def _rating(self, customer_id: str, **data):

        return EpisodicMemory.rating(

            customer_id,

            data["product_id"],

            data["rating"],

        )

    # --------------------------------------------------

    def _feedback(self, customer_id: str, **data):

        return EpisodicMemory.feedback(

            customer_id,

            data["text"],

            data.get("sentiment"),

        )

    # --------------------------------------------------

    def _login(self, customer_id: str, **data):

        return EpisodicMemory(

            customer_id=customer_id,

            event_type="login",

            importance=0.1,

            metadata=data,

        )

    # --------------------------------------------------

    def _recommendation(self, customer_id: str, **data):

        return EpisodicMemory.recommendation(

            customer_id,

            data["recommendation_id"],

            data.get("accepted", False),

        )

    # --------------------------------------------------

    @staticmethod
    def supported_events():

        return [

            event.value

            for event in EventType

        ]

    # --------------------------------------------------

    def health(self):

        return {

            "status": "healthy",

            "supported_events": len(EventType),

        }

    # --------------------------------------------------

    def __repr__(self):

        return (

            f"EventManager("

            f"events={len(EventType)})"

        )


__all__ = [

    "EventType",

    "EventManager",

]