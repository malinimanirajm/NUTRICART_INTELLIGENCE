"""
Nutrition Plugin

Generic nutrient parser.

Supports

✓ protein > 20
✓ protein >= 20
✓ protein below 20
✓ protein between 10 and 20

✓ below 100 calories
✓ above 20 protein
✓ between 100 and 200 calories

✓ aliases
✓ units
✓ natural language

Works for every nutrient in
config.search_config.NUTRIENTS
"""

import re

from config.search_config import NUTRIENTS
from .base_plugin import SearchPlugin


class NutritionPlugin(SearchPlugin):

    def __init__(self):

        self.rules = NUTRIENTS

        #
        # Minimum
        #

        self.min_patterns = [

            r"{name}\s*(>=|>)\s*(\d+(?:\.\d+)?)",

            r"{name}\s*(?:greater than|more than|above|over)\s*(\d+(?:\.\d+)?)",

            r"(?:greater than|more than|above|over)\s*(\d+(?:\.\d+)?)\s*(?:g|gm|grams|mg|cal|kcal|calories)?\s*{name}",

        ]

        #
        # Maximum
        #

        self.max_patterns = [

            r"{name}\s*(<=|<)\s*(\d+(?:\.\d+)?)",

            r"{name}\s*(?:less than|below|under)\s*(\d+(?:\.\d+)?)",

            r"(?:less than|below|under)\s*(\d+(?:\.\d+)?)\s*(?:g|gm|grams|mg|cal|kcal|calories)?\s*{name}",

        ]

        #
        # Between
        #

        self.between_patterns = [

            r"{name}\s*between\s*(\d+(?:\.\d+)?)\s*and\s*(\d+(?:\.\d+)?)",

            r"between\s*(\d+(?:\.\d+)?)\s*and\s*(\d+(?:\.\d+)?)\s*(?:g|gm|grams|mg|cal|kcal|calories)?\s*{name}",

        ]

        #
        # Unit only
        #

        self.unit_patterns = [

            r"(\d+(?:\.\d+)?)\s*(?:g|gm|grams|mg|cal|kcal|calories)\s*{name}"

        ]

    # ---------------------------------------------------------

    def apply(

        self,

        query,

        filters,

    ):

        query = query.lower()

        for nutrient, config in self.rules.items():

            aliases = config.get(

                "aliases",

                [nutrient]

            )

            for alias in aliases:

                self._extract_between(

                    alias,

                    nutrient,

                    query,

                    filters,

                    config,

                )

                self._extract_minimum(

                    alias,

                    nutrient,

                    query,

                    filters,

                    config,

                )

                self._extract_maximum(

                    alias,

                    nutrient,

                    query,

                    filters,

                    config,

                )

                self._extract_units(

                    alias,

                    nutrient,

                    query,

                    filters,

                    config,

                )

        return filters

    # ---------------------------------------------------------

    def _extract_between(

        self,

        alias,

        nutrient,

        query,

        filters,

        config,

    ):

        for pattern in self.between_patterns:

            regex = pattern.format(

                name=re.escape(alias)

            )

            match = re.search(

                regex,

                query,

            )

            if not match:

                continue

            minimum = float(

                match.group(1)

            )

            maximum = float(

                match.group(2)

            )

            setattr(

                filters,

                config["min_filter"],

                minimum,

            )

            setattr(

                filters,

                config["max_filter"],

                maximum,

            )

            setattr(

                filters,

                f"{nutrient}_min_operator",

                ">=",

            )

            setattr(

                filters,

                f"{nutrient}_max_operator",

                "<=",

            )

            return
        # ---------------------------------------------------------

    def _extract_minimum(

        self,

        alias,

        nutrient,

        query,

        filters,

        config,

    ):

        for pattern in self.min_patterns:

            regex = pattern.format(

                name=re.escape(alias)

            )

            match = re.search(

                regex,

                query,

            )

            if not match:

                continue

            #
            # protein > 20
            #

            if len(match.groups()) == 2:

                operator = match.group(1)

                value = float(

                    match.group(2)

                )

            #
            # protein above 20
            #

            else:

                operator = ">"

                value = float(

                    match.group(1)

                )

            self._set_min(

                nutrient,

                filters,

                config,

                value,

                operator,

            )

            return

    # ---------------------------------------------------------

    def _extract_maximum(

        self,

        alias,

        nutrient,

        query,

        filters,

        config,

    ):

        for pattern in self.max_patterns:

            regex = pattern.format(

                name=re.escape(alias)

            )

            match = re.search(

                regex,

                query,

            )

            if not match:

                continue

            #
            # protein < 20
            #

            if len(match.groups()) == 2:

                operator = match.group(1)

                value = float(

                    match.group(2)

                )

            #
            # protein below 20
            #

            else:

                operator = "<"

                value = float(

                    match.group(1)

                )

            self._set_max(

                nutrient,

                filters,

                config,

                value,

                operator,

            )

            return

    # ---------------------------------------------------------

    def _set_min(

        self,

        nutrient,

        filters,

        config,

        value,

        operator,

    ):

        setattr(

            filters,

            config["min_filter"],

            value,

        )

        setattr(

            filters,

            f"{nutrient}_min_operator",

            operator,

        )

    # ---------------------------------------------------------

    def _set_max(

        self,

        nutrient,

        filters,

        config,

        value,

        operator,

    ):

        setattr(

            filters,

            config["max_filter"],

            value,

        )

        setattr(

            filters,

            f"{nutrient}_max_operator",

            operator,

        )
        # ---------------------------------------------------------

    def _extract_units(

        self,

        alias,

        nutrient,

        query,

        filters,

        config,

    ):

        """
        Handles

        20g protein
        100 calories
        100 kcal
        500 mg sodium
        """

        #
        # Don't overwrite values already
        # extracted by between/min/max.
        #

        if getattr(filters, config["min_filter"]) is not None:
            return

        if getattr(filters, config["max_filter"]) is not None:
            return

        for pattern in self.unit_patterns:

            regex = pattern.format(

                name=re.escape(alias)

            )

            match = re.search(

                regex,

                query,

            )

            if not match:
                continue

            value = float(

                match.group(1)

            )

            #
            # Default interpretation:
            #
            # "20g protein"
            #
            # means
            #
            # protein >= 20
            #

            self._set_min(

                nutrient,

                filters,

                config,

                value,

                ">=",

            )

            return

    # ---------------------------------------------------------

    @staticmethod
    def _contains_number(

        text,

    ):

        return bool(

            re.search(

                r"\d",

                text,

            )

        )

    # ---------------------------------------------------------

    @staticmethod
    def _normalize_spaces(

        text,

    ):

        return re.sub(

            r"\s+",

            " ",

            text,

        ).strip()