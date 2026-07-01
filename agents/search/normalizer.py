"""
Query Normalizer

Responsibilities
----------------
1. Lowercase query
2. Remove extra spaces
3. Correct common spelling mistakes
4. Normalize comparison operators
5. Normalize common phrases

No parsing.
No business logic.
"""

import re


class QueryNormalizer:

    def __init__(self):

        self.typos = {

            # Categories
            "bevrages": "beverages",
            "beveragess": "beverages",
            "snaks": "snacks",
            "coockies": "cookies",
            "cookes": "cookies",
            "dairry": "dairy",

            # Nutrition
            "protien": "protein",
            "protin": "protein",
            "protine": "protein",
            "suger": "sugar",
            "calory": "calories",
            "calorie": "calories",

        }

        self.synonyms = {

            "high protein": "protein greater than 15g",

            "low sugar": "sugar less than 5g",

            "sugar free": "sugar less than 1g"

        }

    # --------------------------------------------------

    def normalize(self, query: str) -> str:

        query = query.lower()

        query = self._remove_extra_spaces(query)

        query = self._fix_typos(query)

        query = self._normalize_symbols(query)

        query = self._replace_synonyms(query)

        return query

    # --------------------------------------------------

    def _remove_extra_spaces(self, text):

        return re.sub(r"\s+", " ", text).strip()

    # --------------------------------------------------

    def _fix_typos(self, text):

        for wrong, correct in self.typos.items():

            text = text.replace(wrong, correct)

        return text

    # --------------------------------------------------

    def _replace_synonyms(self, text):

        for old, new in self.synonyms.items():

            text = text.replace(old, new)

        return text

    # --------------------------------------------------

    def _normalize_symbols(self, text):

        replacements = {

            ">=": " greater_or_equal ",

            "<=": " less_or_equal ",

            ">": " greater_than ",

            "<": " less_than "

        }

        for old, new in replacements.items():

            text = text.replace(old, new)

        return self._remove_extra_spaces(text)