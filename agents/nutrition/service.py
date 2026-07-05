"""
agents/nutrition/service.py
"""

from __future__ import annotations

from agents.order.service import OrderService
from agents.nutrition.calculator import NutritionCalculator
from agents.nutrition.models import (
    NutritionReport,
)


class NutritionService:

    def __init__(self):

        self.orders = OrderService()

        self.calculator = NutritionCalculator()

    # =====================================================

    def daily_summary(
        self,
        customer_id: str,
    ) -> NutritionReport:

        orders = self.orders.daily_orders(
            customer_id
        )

        summary = self.calculator.calculate(
            orders
        )

        return NutritionReport(

            period="Daily",

            total_orders=len(orders),

            summary=summary,

        )

    # =====================================================

    def weekly_summary(
        self,
        customer_id: str,
    ) -> NutritionReport:

        orders = self.orders.weekly_orders(
            customer_id
        )

        summary = self.calculator.calculate(
            orders
        )

        return NutritionReport(

            period="Weekly",

            total_orders=len(orders),

            summary=summary,

        )

    # =====================================================

    def monthly_summary(
        self,
        customer_id: str,
    ) -> NutritionReport:

        orders = self.orders.monthly_orders(
            customer_id
        )

        summary = self.calculator.calculate(
            orders
        )

        return NutritionReport(

            period="Monthly",

            total_orders=len(orders),

            summary=summary,

        )

    # =====================================================

    def yearly_summary(
        self,
        customer_id: str,
    ) -> NutritionReport:

        orders = self.orders.yearly_orders(
            customer_id
        )

        summary = self.calculator.calculate(
            orders
        )

        return NutritionReport(

            period="Yearly",

            total_orders=len(orders),

            summary=summary,

        )