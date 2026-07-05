"""
Product Validator

Responsibilities
----------------
1. Validate mandatory fields
2. Validate nutrition values
3. Validate duplicate products
4. Return ValidationResult

No Weaviate.
No CSV loading.
No transformations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


# ==========================================================
# Validation Result
# ==========================================================

@dataclass
class ValidationResult:

    valid: bool = True

    errors: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)


# ==========================================================
# Product Validator
# ==========================================================

class ProductValidator:

    def __init__(self):

        self.seen_products = set()

        self.numeric_fields = [

            "protein_g",
            "fat_g",
            "fiber_g",
            "carbs_g",
            "healthy_fat_g",
            "saturated_fat_g",
            "added_sugar_g",
            "sodium_mg",
            "potassium_mg",
            "calories_100g"

        ]

    # -----------------------------------------------------

    def validate(
        self,
        document: dict
    ) -> ValidationResult:

        result = ValidationResult()

        self._validate_required_fields(
            document,
            result
        )

        self._validate_duplicate(
            document,
            result
        )

        self._validate_numeric_fields(
            document,
            result
        )

        self._validate_boolean_fields(
            document,
            result
        )

        return result

    # -----------------------------------------------------

    def _validate_required_fields(
        self,
        document,
        result
    ):

        required = [

            "product_id",

            "product_name",

            "category_name",

            "brand_name"

        ]

        for field in required:

            value = document.get(field)

            if value is None or value == "":

                result.valid = False

                result.errors.append(

                    f"{field} is required"

                )

    # -----------------------------------------------------

    def _validate_duplicate(
        self,
        document,
        result
    ):

        product_id = document.get("product_id")

        if product_id in self.seen_products:

            result.valid = False

            result.errors.append(

                f"Duplicate product_id '{product_id}'"

            )

            return

        self.seen_products.add(product_id)

    # -----------------------------------------------------

    def _validate_numeric_fields(
        self,
        document,
        result
    ):

        for field in self.numeric_fields:

            value = document.get(field)

            if value is None:

                continue

            if not isinstance(value, (int, float)):

                result.valid = False

                result.errors.append(

                    f"{field} must be numeric"

                )

                continue

            if value < 0:

                result.valid = False

                result.errors.append(

                    f"{field} cannot be negative"

                )

    # -----------------------------------------------------

    def _validate_boolean_fields(
        self,
        document,
        result
    ):

        boolean_fields = [

            "is_organic_available",

            "is_whole_grain",

            "is_refined_grain",

            "has_artificial_additives",

            "deep_fried"

        ]

        for field in boolean_fields:

            value = document.get(field)

            if value is None:

                continue

            if not isinstance(value, bool):

                result.valid = False

                result.errors.append(

                    f"{field} must be boolean"

                )