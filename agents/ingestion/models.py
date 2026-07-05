"""
Product Document Models

Responsibilities
----------------
1. Product search document
2. Typed ingestion model

No Weaviate.
No CSV.
No business logic.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ProductDocument:

    # -----------------------------------------------------
    # Identity
    # -----------------------------------------------------

    product_id: str

    product_name: str

    # -----------------------------------------------------
    # Category
    # -----------------------------------------------------

    category_id: int

    category_name: str

    processing_level: str

    # -----------------------------------------------------
    # Brand
    # -----------------------------------------------------

    brand_id: int

    brand_name: str

    brand_type: str

    # -----------------------------------------------------
    # Organic
    # -----------------------------------------------------

    is_organic_available: bool

    # -----------------------------------------------------
    # Nutrition
    # -----------------------------------------------------

    calories_100g: float

    carbs_g: float

    fiber_g: float

    protein_g: float

    fat_g: float

    healthy_fat_g: float

    saturated_fat_g: float

    added_sugar_g: float

    sodium_mg: float

    potassium_mg: float

    is_whole_grain: bool

    is_refined_grain: bool

    has_artificial_additives: bool

    deep_fried: bool

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    search_text: str