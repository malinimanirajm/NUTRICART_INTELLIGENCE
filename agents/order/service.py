"""
agents/order/service.py
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from agents.order.models import Order
from agents.order.models import OrderItem
from agents.order.repository import OrderRepository
from agents.search.repository import SearchRepository


class OrderService:

    def __init__(self):

        self.repository = OrderRepository()

        self.products = SearchRepository()

    # =====================================================

    def place_order(
        self,
        customer_id: str,
        items: list[tuple[str, int]],
    ) -> Order:

        order_items = []

        for product_id, quantity in items:

            product = self.products.get_product(
                product_id
            )

            if product is None:

                raise ValueError(
                    f"Unknown product: {product_id}"
                )

            order_items.append(

                OrderItem(

                    product_id=product["product_id"],

                    product_name=product["product_name"],

                    quantity=quantity,

                    protein=float(
                        product.get(
                            "protein_g",
                            0,
                        )
                    ),

                    calories=float(
                        product.get(
                            "calories_100g",
                            0,
                        )
                    ),

                    sugar=float(
                        product.get(
                            "added_sugar_g",
                            0,
                        )
                    ),

                    fat=float(
                        product.get(
                            "fat_g",
                            0,
                        )
                    ),

                    fiber=float(
                        product.get(
                            "fiber_g",
                            0,
                        )
                    ),

                    sodium=float(
                        product.get(
                            "sodium_mg",
                            0,
                        )
                    ),

                    potassium=float(
                        product.get(
                            "potassium_mg",
                            0,
                        )
                    ),

                )

            )

        order = Order(

            order_id=str(uuid4()),

            customer_id=customer_id,

            ordered_at=datetime.now(),

            items=order_items,

        )

        self.repository.place_order(
            order
        )

        return order

    # =====================================================

    def get_orders(
        self,
        customer_id: str,
    ):

        return self.repository.get_orders(
            customer_id
        )

    # =====================================================

    def daily_orders(
        self,
        customer_id: str,
    ):

        end = datetime.now()

        start = datetime(
            end.year,
            end.month,
            end.day,
        )

        return self.repository.get_orders_between(

            customer_id,

            start,

            end,

        )

    # =====================================================

    def weekly_orders(
        self,
        customer_id: str,
    ):

        end = datetime.now()

        start = end - timedelta(days=7)

        return self.repository.get_orders_between(

            customer_id,

            start,

            end,

        )

    # =====================================================

    def monthly_orders(
        self,
        customer_id: str,
    ):

        end = datetime.now()

        start = end - timedelta(days=30)

        return self.repository.get_orders_between(

            customer_id,

            start,

            end,

        )

    # =====================================================

    def yearly_orders(
        self,
        customer_id: str,
    ):

        end = datetime.now()

        start = end - timedelta(days=365)

        return self.repository.get_orders_between(

            customer_id,

            start,

            end,

        )