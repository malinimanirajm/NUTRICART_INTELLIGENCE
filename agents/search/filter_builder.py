"""
Generic Weaviate Filter Builder

Converts SearchFilters into Weaviate Filters.
"""

from functools import reduce
from operator import and_

from weaviate.classes.query import Filter

from config.search_config import (
    NUTRIENTS,
    PREFERENCES,
)


class FilterBuilder:

    def __init__(self):

        self.nutrients = NUTRIENTS
        self.preferences = PREFERENCES

    # -----------------------------------------------------

    def build(self, filters):

        expressions = []

        #
        # Category
        #

        if filters.category:

            expressions.append(

                Filter.by_property(
                    "category_name"
                ).equal(filters.category)

            )

        #
        # Brand
        #

        if filters.brand:

            expressions.append(

                Filter.by_property(
                    "brand_name"
                ).equal(filters.brand)

            )

        #
        # Nutrition
        #

        expressions.extend(

            self._nutrition_filters(filters)

        )

        #
        # Dietary Preferences
        #

        expressions.extend(

            self._preference_filters(filters)

        )

        if not expressions:

            return None

        return reduce(and_, expressions)

    # -----------------------------------------------------

    def _nutrition_filters(self, filters):

        expressions = []

        for nutrient, config in self.nutrients.items():

            db_field = config["db_field"]

            minimum = getattr(

                filters,

                config["min_filter"],

            )

            maximum = getattr(

                filters,

                config["max_filter"],

            )

            min_operator = getattr(

                filters,

                f"{nutrient}_min_operator",

                ">=",

            )

            max_operator = getattr(

                filters,

                f"{nutrient}_max_operator",

                "<=",

            )

            #
            # Minimum
            #

            if minimum is not None:

                expressions.append(

                    self._comparison(

                        db_field,

                        minimum,

                        min_operator,

                    )

                )

            #
            # Maximum
            #

            if maximum is not None:

                expressions.append(

                    self._comparison(

                        db_field,

                        maximum,

                        max_operator,

                    )

                )

        return expressions

    # -----------------------------------------------------

    def _preference_filters(self, filters):

        expressions = []

        #
        # SearchFilters attribute
        #          ↓
        # Weaviate Property
        #

        preference_map = {

            "organic": "is_organic_available",

            "vegan": "is_vegan",

            "gluten_free": "is_gluten_free",

            "diabetic": "diabetic_friendly",

            #
            # Future Features
            #

            "heart_healthy": "heart_healthy",

            "high_protein": "high_protein",

            "low_sugar": "low_sugar",

        }

        for attribute, property_name in preference_map.items():

            #
            # Skip attributes that don't
            # exist yet in SearchFilters.
            #

            if not hasattr(filters, attribute):

                continue

            if getattr(filters, attribute):

                expressions.append(

                    Filter.by_property(

                        property_name

                    ).equal(True)

                )

        return expressions

    # -----------------------------------------------------

    def _comparison(

        self,

        property_name,

        value,

        operator,

    ):

        if operator == ">":

            return (

                Filter.by_property(

                    property_name

                ).greater_than(value)

            )

        if operator == ">=":

            return (

                Filter.by_property(

                    property_name

                ).greater_or_equal(value)

            )

        if operator == "<":

            return (

                Filter.by_property(

                    property_name

                ).less_than(value)

            )

        if operator == "<=":

            return (

                Filter.by_property(

                    property_name

                ).less_or_equal(value)

            )

        raise ValueError(

            f"Unsupported operator: {operator}"

        )