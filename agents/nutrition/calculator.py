"""
agents/nutrition/calculator.py
"""

from __future__ import annotations

from agents.nutrition.models import NutritionSummary


class NutritionCalculator:

    """
    Calculates nutrition statistics from customer orders.
    """

    # =====================================================

    def calculate(
        self,
        orders,
    ) -> NutritionSummary:

        summary = NutritionSummary()

        if not orders:
            return summary

        highest_protein = 0.0
        lowest_protein = float("inf")

        total_items = 0

        for order in orders:

            order_protein = 0.0

            for item in order.items:

                quantity = item.quantity

                total_items += quantity

                protein = item.protein * quantity
                calories = item.calories * quantity
                sugar = item.sugar * quantity
                fat = item.fat * quantity
                fiber = item.fiber * quantity
                sodium = item.sodium * quantity
                potassium = item.potassium * quantity

                summary.protein += protein
                summary.calories += calories
                summary.sugar += sugar
                summary.fat += fat
                summary.fiber += fiber
                summary.sodium += sodium
                summary.potassium += potassium

                order_protein += protein

            highest_protein = max(
                highest_protein,
                order_protein,
            )

            lowest_protein = min(
                lowest_protein,
                order_protein,
            )

        summary.total_items = total_items
        summary.total_orders = len(orders)

        summary.average_protein = round(
            summary.protein / len(orders),
            2,
        )

        summary.average_calories = round(
            summary.calories / len(orders),
            2,
        )

        summary.highest_protein_order = round(
            highest_protein,
            2,
        )

        summary.lowest_protein_order = round(
            0
            if lowest_protein == float("inf")
            else lowest_protein,
            2,
        )

        return summary