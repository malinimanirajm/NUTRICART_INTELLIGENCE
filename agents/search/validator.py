"""
Search Validator

Responsibilities
----------------
1. Validate extracted filters.
2. Validate category and brand.
3. Validate nutrition ranges.
4. Normalize values.
5. Return ValidationResult.

No Weaviate queries.
No Parser.
No Memory.
"""

from dataclasses import dataclass, field
from typing import List

from config.dictionary_loader import CACHE

from agents.search.filters import SearchFilters


# ---------------------------------------------------------
# Validation Result
# ---------------------------------------------------------

@dataclass
class ValidationResult:

    filters: SearchFilters

    valid: bool = True

    errors: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)


# ---------------------------------------------------------
# Validator
# ---------------------------------------------------------

class SearchValidator:

    def __init__(self):

        self.categories = set(CACHE["categories"].values())

        self.brands = set(CACHE["brands"].values())

    # -----------------------------------------------------

    def validate(
        self,
        filters: SearchFilters
    ) -> ValidationResult:

        result = ValidationResult(filters=filters)

        self._validate_category(result)

        self._validate_brand(result)

        self._validate_numeric_ranges(result)

        self._validate_positive_numbers(result)

        return result

    # -----------------------------------------------------

    def _validate_category(self, result):

        category = result.filters.category

        if category is None:
            return

        if category not in self.categories:

            result.valid = False

            result.errors.append(
                f"Unknown category '{category}'"
            )

    # -----------------------------------------------------

    def _validate_brand(self, result):

        brand = result.filters.brand

        if brand is None:
            return

        if brand not in self.brands:

            result.valid = False

            result.errors.append(
                f"Unknown brand '{brand}'"
            )

    # -----------------------------------------------------

    def _validate_numeric_ranges(self, result):

        pairs = [

            ("protein",
             result.filters.min_protein,
             result.filters.max_protein),

            ("sugar",
             result.filters.min_sugar,
             result.filters.max_sugar),

            ("calories",
             result.filters.min_calories,
             result.filters.max_calories),

            ("fat",
             result.filters.min_fat,
             result.filters.max_fat),

            ("fiber",
             result.filters.min_fiber,
             result.filters.max_fiber),

            ("sodium",
             result.filters.min_sodium,
             result.filters.max_sodium)

        ]

        for nutrient, minimum, maximum in pairs:

            if minimum is None or maximum is None:
                continue

            if minimum > maximum:

                result.valid = False

                result.errors.append(

                    f"{nutrient}: minimum cannot be greater than maximum"

                )

    # -----------------------------------------------------

    def _validate_positive_numbers(self, result):

        values = [

            ("protein", result.filters.min_protein),
            ("protein", result.filters.max_protein),

            ("sugar", result.filters.min_sugar),
            ("sugar", result.filters.max_sugar),

            ("calories", result.filters.min_calories),
            ("calories", result.filters.max_calories),

            ("fat", result.filters.min_fat),
            ("fat", result.filters.max_fat),

            ("fiber", result.filters.min_fiber),
            ("fiber", result.filters.max_fiber),

            ("sodium", result.filters.min_sodium),
            ("sodium", result.filters.max_sodium)

        ]

        for nutrient, value in values:

            if value is None:
                continue

            if value < 0:

                result.valid = False

                result.errors.append(

                    f"{nutrient} cannot be negative"

                )