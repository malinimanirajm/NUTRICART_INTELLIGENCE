"""
Dictionary Loader

Responsibilities
----------------
1. Load product metadata from Weaviate.
2. Build category lookup.
3. Build brand lookup.
4. Cache dictionaries.
5. Refresh cache when required.
"""

import weaviate


class DictionaryLoader:

    def __init__(self):

        self.client = weaviate.connect_to_local()

        self.collection = self.client.collections.get(
            "NutricartUnified"
        )

    # -----------------------------------------------------

    def load(self):

        response = self.collection.query.fetch_objects(
            limit=10000
        )

        category_lookup = {}

        brand_lookup = {}

        for obj in response.objects:

            props = obj.properties

            self._add_category(
                props,
                category_lookup
            )

            self._add_brand(
                props,
                brand_lookup
            )

        return {

            "categories": category_lookup,

            "brands": brand_lookup

        }

    # -----------------------------------------------------

    def _add_category(
        self,
        props,
        lookup
    ):

        category = props.get("category_name")

        if not category:
            return

        self._build_aliases(
            category,
            lookup
        )

    # -----------------------------------------------------

    def _add_brand(
        self,
        props,
        lookup
    ):

        brand = props.get("brand_name")

        if not brand:
            return

        self._build_aliases(
            brand,
            lookup
        )

    # -----------------------------------------------------

    def _build_aliases(
        self,
        value,
        lookup
    ):

        value = value.strip()

        canonical = value

        text = value.lower()

        aliases = set()

        aliases.add(text)

        aliases.add(
            text.replace(" ", "")
        )

        aliases.add(
            text.replace("-", " ")
        )

        words = text.split()

        aliases.update(words)

        if text.endswith("s"):

            aliases.add(text[:-1])

        else:

            aliases.add(text + "s")

        if len(words) > 1:

            aliases.add(" ".join(words))

            for word in words:

                aliases.add(word)

        for alias in aliases:

            lookup[alias] = canonical

    # -----------------------------------------------------

    def refresh(self):

        global CACHE

        CACHE = self.load()

    # -----------------------------------------------------

    def close(self):

        self.client.close()


# ---------------------------------------------------------
# Global Cache
# ---------------------------------------------------------

loader = DictionaryLoader()
try:
    CACHE = loader.load()
finally:
    loader.close()
