"""
Generic Nutrition Plugin

Supports all nutrients configured in search_config.py

Examples

protein > 20
protein >= 20
protein < 20
protein <= 20

protein greater than 20
greater than 20g protein

protein between 20 and 30
between 20 and 30 protein

protein 20-30

at least 20g protein
at most 5g sugar
"""

import re

from .base_plugin import SearchPlugin


class NutritionPlugin(SearchPlugin):

    def __init__(self, nutrient_rules):

        self.rules = nutrient_rules

    # --------------------------------------------------

    def apply(self, query, filters):

        query = query.lower()

        for nutrient, config in self.rules.items():

            self._extract(

                nutrient,

                config,

                query,

                filters

            )

    # --------------------------------------------------

    def _extract(

        self,

        nutrient,

        config,

        query,

        filters

    ):

        min_field = config["min_filter"]

        max_field = config["max_filter"]

        min_operator_field = f"{nutrient}_min_operator"

        max_operator_field = f"{nutrient}_max_operator"

        # ====================================================
        # calories between 100 and 200
        # protein between 20 and 30
        # ====================================================

        match = re.search(

            rf"{nutrient}\s+between\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)",

            query

        )

        if match:

            setattr(filters, min_field, float(match.group(1)))
            setattr(filters, max_field, float(match.group(2)))

            return

        # ====================================================
        # between 100 and 200 calories
        # between 20 and 30 protein
        # ====================================================

        match = re.search(

            rf"between\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)\s+{nutrient}",

            query

        )

        if match:

            setattr(filters, min_field, float(match.group(1)))
            setattr(filters, max_field, float(match.group(2)))

            return

        # ====================================================
        # protein 20-30
        # ====================================================

        match = re.search(

            rf"{nutrient}\s+(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)",

            query

        )

        if match:

            setattr(filters, min_field, float(match.group(1)))
            setattr(filters, max_field, float(match.group(2)))

            return

        # ====================================================
        # Comparison Patterns
        # ====================================================

        patterns = [

            # protein >20

            (rf"{nutrient}\s*>\s*(\d+(?:\.\d+)?)",
             min_field,
             min_operator_field,
             ">"),

            # protein >=20

            (rf"{nutrient}\s*>=\s*(\d+(?:\.\d+)?)",
             min_field,
             min_operator_field,
             ">="),

            # protein <20

            (rf"{nutrient}\s*<\s*(\d+(?:\.\d+)?)",
             max_field,
             max_operator_field,
             "<"),

            # protein <=20

            (rf"{nutrient}\s*<=\s*(\d+(?:\.\d+)?)",
             max_field,
             max_operator_field,
             "<="),

            # protein greater than 20

            (rf"{nutrient}\s+greater than\s+(\d+(?:\.\d+)?)",
             min_field,
             min_operator_field,
             ">"),

            # protein more than 20

            (rf"{nutrient}\s+more than\s+(\d+(?:\.\d+)?)",
             min_field,
             min_operator_field,
             ">"),

            # protein above 20

            (rf"{nutrient}\s+above\s+(\d+(?:\.\d+)?)",
             min_field,
             min_operator_field,
             ">"),

            # protein over 20

            (rf"{nutrient}\s+over\s+(\d+(?:\.\d+)?)",
             min_field,
             min_operator_field,
             ">"),

            # protein less than 20

            (rf"{nutrient}\s+less than\s+(\d+(?:\.\d+)?)",
             max_field,
             max_operator_field,
             "<"),

            # protein below 20

            (rf"{nutrient}\s+below\s+(\d+(?:\.\d+)?)",
             max_field,
             max_operator_field,
             "<"),

            # protein under 20

            (rf"{nutrient}\s+under\s+(\d+(?:\.\d+)?)",
             max_field,
             max_operator_field,
             "<"),

            # greater than 20g protein

            (rf"greater than\s+(\d+(?:\.\d+)?)g?\s*{nutrient}",
             min_field,
             min_operator_field,
             ">"),

            # less than 5g sugar

            (rf"less than\s+(\d+(?:\.\d+)?)g?\s*{nutrient}",
             max_field,
             max_operator_field,
             "<"),

            # at least

            (rf"at least\s+(\d+(?:\.\d+)?)g?\s*{nutrient}",
             min_field,
             min_operator_field,
             ">="),

            # at most

            (rf"at most\s+(\d+(?:\.\d+)?)g?\s*{nutrient}",
             max_field,
             max_operator_field,
             "<=")

        ]

        for pattern, field, operator_field, operator in patterns:

            match = re.search(pattern, query)

            if match:

                setattr(

                    filters,

                    field,

                    float(match.group(1))

                )

                setattr(

                    filters,

                    operator_field,

                    operator

                )

                return