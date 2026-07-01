"""
Filter Builder

Converts SearchFilters into Weaviate Filters.

Responsibilities
----------------
1. Category Filter
2. Brand Filter
3. Nutrition Filters
4. Preference Filters

No Parsing
No Repository
"""

from dataclasses import asdict

from weaviate.classes.query import Filter

from config.search_config import NUTRIENTS

from agents.search.filters import SearchFilters


class FilterBuilder:

    # -------------------------------------------------

    def build(
        self,
        filters: SearchFilters
    ):

        expressions = []

        data = asdict(filters)

        # ============================================
        # Category
        # ============================================

        if filters.category:

            expressions.append(

                Filter.by_property(
                    "category_name"
                ).equal(
                    filters.category
                )

            )

        # ============================================
        # Brand
        # ============================================

        if filters.brand:

            expressions.append(

                Filter.by_property(
                    "brand_name"
                ).equal(
                    filters.brand
                )

            )

        # ============================================
        # Nutrition
        # ============================================

        for nutrient, config in NUTRIENTS.items():

            db_field = config["db_field"]

            min_filter = config["min_filter"]

            max_filter = config["max_filter"]

            min_operator = data.get(

                f"{nutrient}_min_operator",

                ">="

            )

            max_operator = data.get(

                f"{nutrient}_max_operator",

                "<="

            )

            # -----------------------
            # Minimum
            # -----------------------

            if data[min_filter] is not None:

                expr = Filter.by_property(db_field)

                if min_operator == ">":

                    expr = expr.greater_than(

                        data[min_filter]

                    )

                else:

                    expr = expr.greater_or_equal(

                        data[min_filter]

                    )

                expressions.append(expr)

            # -----------------------
            # Maximum
            # -----------------------

            if data[max_filter] is not None:

                expr = Filter.by_property(db_field)

                if max_operator == "<":

                    expr = expr.less_than(

                        data[max_filter]

                    )

                else:

                    expr = expr.less_or_equal(

                        data[max_filter]

                    )

                expressions.append(expr)

        # ============================================
        # Preferences
        # ============================================

        #
        # Dataset currently has no
        #
        # vegan
        # organic
        # gluten_free
        #
        # properties.
        #
        # Enable once schema supports them.
        #

        if filters.diabetic:

            expressions.append(

                Filter.by_property(

                    "added_sugar_g"

                ).less_or_equal(

                    5

                )

            )

        # Uncomment later
        #
        # if filters.vegan:
        #
        #     expressions.append(
        #
        #         Filter.by_property(
        #
        #             "is_vegan"
        #
        #         ).equal(True)
        #
        #     )
        #
        #
        # if filters.organic:
        #
        #     expressions.append(
        #
        #         Filter.by_property(
        #
        #             "is_organic"
        #
        #         ).equal(True)
        #
        #     )
        #
        #
        # if filters.gluten_free:
        #
        #     expressions.append(
        #
        #         Filter.by_property(
        #
        #             "is_gluten_free"
        #
        #         ).equal(True)
        #
        #     )

        # ============================================
        # No Filters
        # ============================================

        if not expressions:

            return None

        result = expressions[0]

        for expression in expressions[1:]:

            result &= expression

        return result