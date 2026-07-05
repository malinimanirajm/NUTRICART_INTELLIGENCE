"""
Recommendation Models
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ==========================================================
# Customer Profile
# ==========================================================

@dataclass
class CustomerProfile:

    customer_id: str

    #
    # Learned Preferences
    #

    favourite_categories: list[str] = field(default_factory=list)

    favourite_brands: list[str] = field(default_factory=list)

    #
    # Confidence Maps
    #

    category_confidence: dict[str, float] = field(
        default_factory=dict
    )

    brand_confidence: dict[str, float] = field(
        default_factory=dict
    )

    #
    # Nutrition Preferences
    #

    preferred_protein: Optional[float] = None

    preferred_calories: Optional[float] = None

    preferred_sugar: Optional[float] = None

    #
    # Dietary Preferences
    #

    diabetic: bool = False

    vegan: bool = False

    gluten_free: bool = False

    organic: bool = False

    #
    # Shopping Behaviour
    #

    average_order_value: float = 0.0

    average_products_per_order: float = 0.0


# ==========================================================
# Recommendation Candidate
# ==========================================================

@dataclass
class Recommendation:

    product: dict

    score: float = 0.0

    reasons: list[str] = field(default_factory=list)


# ==========================================================
# Recommendation Result
# ==========================================================

@dataclass
class RecommendationResult:

    customer_id: str

    query: str

    recommendations: list[Recommendation] = field(
        default_factory=list
    )

    status: str = "success"

    message: str = ""


# ==========================================================
# Recommendation Context
# ==========================================================

@dataclass
class RecommendationContext:

    customer_profile: CustomerProfile

    query: str

    candidate_products: list[dict]