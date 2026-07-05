"""
agents/order/repository.py
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from agents.order.models import Order


class OrderRepository:

    def __init__(
        self,
        database: str = "memory.db",
    ):

        self.connection = sqlite3.connect(database)
        self.connection.row_factory = sqlite3.Row

        self._create_table()

    # =====================================================

    def _create_table(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customer_orders (

                order_id TEXT PRIMARY KEY,

                customer_id TEXT NOT NULL,

                ordered_at TEXT NOT NULL,

                data TEXT NOT NULL

            )
            """
        )

        self.connection.commit()

    # =====================================================

    def place_order(
        self,
        order: Order,
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO customer_orders
            VALUES (?, ?, ?, ?)
            """,
            (
                order.order_id,
                order.customer_id,
                order.ordered_at.isoformat(),
                json.dumps(order.to_dict()),
            ),
        )

        self.connection.commit()

    # =====================================================

    def get_orders(
        self,
        customer_id: str,
    ) -> list[Order]:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT data
            FROM customer_orders
            WHERE customer_id=?
            ORDER BY ordered_at DESC
            """,
            (customer_id,),
        )

        rows = cursor.fetchall()

        return [

            Order.from_dict(
                json.loads(row["data"])
            )

            for row in rows

        ]

    # =====================================================

    def get_orders_between(
        self,
        customer_id: str,
        start: datetime,
        end: datetime,
    ) -> list[Order]:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT data
            FROM customer_orders
            WHERE customer_id=?
            AND ordered_at>=?
            AND ordered_at<=?
            ORDER BY ordered_at DESC
            """,
            (
                customer_id,
                start.isoformat(),
                end.isoformat(),
            ),
        )

        rows = cursor.fetchall()

        return [

            Order.from_dict(
                json.loads(row["data"])
            )

            for row in rows

        ]

    # =====================================================

    def get_last_order(
        self,
        customer_id: str,
    ) -> Order | None:

        orders = self.get_orders(customer_id)

        if not orders:
            return None

        return orders[0]