"""
Dietary Rules

Contains business rules for classifying products.

The transformer should only call these methods.
"""


class DietaryRules:

    # -----------------------------------------------------

    @staticmethod
    def diabetic_friendly(product: dict) -> bool:
        """
        Conservative rule.

        Low sugar
        Moderate calories
        High fiber
        """

        sugar = product.get("added_sugar_g", 0)
        fiber = product.get("fiber_g", 0)
        calories = product.get("calories_100g", 0)

        return (

            sugar <= 5

            and

            fiber >= 3

            and

            calories <= 250

        )

    # -----------------------------------------------------

    @staticmethod
    def vegan(product: dict) -> bool:

        category = product.get("category_name", "").lower()

        non_vegan = {

            "dairy",

            "meat",

            "seafood",

            "egg",

            "eggs",

        }

        return category not in non_vegan

    # -----------------------------------------------------

    @staticmethod
    def gluten_free(product: dict) -> bool:

        return not product.get(

            "is_refined_grain",

            False,

        )

    # -----------------------------------------------------

    @staticmethod
    def heart_healthy(product: dict) -> bool:

        return (

            product.get("saturated_fat_g", 0) <= 2

            and

            product.get("sodium_mg", 0) <= 200

        )

    # -----------------------------------------------------

    @staticmethod
    def high_protein(product: dict) -> bool:

        return product.get(

            "protein_g",

            0,

        ) >= 15

    # -----------------------------------------------------

    @staticmethod
    def low_sugar(product: dict) -> bool:

        return product.get(

            "added_sugar_g",

            0,

        ) <= 5