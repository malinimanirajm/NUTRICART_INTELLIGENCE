"""
agents/order/models.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


# ==========================================================
# Order Item
# ==========================================================

@dataclass
class OrderItem:

    product_id: str

    product_name: str

    quantity: int = 1

    protein: float = 0.0

    calories: float = 0.0

    sugar: float = 0.0

    fat: float = 0.0

    fiber: float = 0.0

    sodium: float = 0.0

    potassium: float = 0.0


# ==========================================================
# Order
# ==========================================================

@dataclass
class Order:

    order_id: str

    customer_id: str

    ordered_at: datetime

    items: list[OrderItem] = field(default_factory=list)

    # -----------------------------------------------------

    def to_dict(self):

        return {

            "order_id": self.order_id,

            "customer_id": self.customer_id,

            "ordered_at": self.ordered_at.isoformat(),

            "items": [

                item.__dict__

                for item in self.items

            ],

        }

    # -----------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ):

        return cls(

            order_id=data["order_id"],

            customer_id=data["customer_id"],

            ordered_at=datetime.fromisoformat(
                data["ordered_at"]
            ),

            items=[

                OrderItem(**item)

                for item in data["items"]

            ],

        )