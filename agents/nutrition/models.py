"""
agents/nutrition/models.py
"""

from __future__ import annotations

from dataclasses import dataclass


# ==========================================================
# Nutrition Summary
# ==========================================================

from dataclasses import dataclass, field


@dataclass
class NutritionSummary:

    protein: float = 0.0
    calories: float = 0.0
    sugar: float = 0.0
    fat: float = 0.0
    fiber: float = 0.0
    sodium: float = 0.0
    potassium: float = 0.0

    total_items: int = 0
    total_orders: int = 0

    average_protein: float = 0.0
    average_calories: float = 0.0

    highest_protein_order: float = 0.0
    lowest_protein_order: float = 0.0

    top_categories: dict[str, int] = field(
        default_factory=dict
    )

    top_brands: dict[str, int] = field(
        default_factory=dict
    )

# ==========================================================
# Nutrition Report
# ==========================================================

@dataclass
class NutritionReport:

    period: str

    total_orders: int

    summary: NutritionSummary