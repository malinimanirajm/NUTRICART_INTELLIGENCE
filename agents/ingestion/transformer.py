"""
Product Transformer

Responsibilities
----------------
1. Join product master data
2. Join nutrition data
3. Join category data
4. Join brand data
5. Build searchable document
"""

from __future__ import annotations

from agents.ingestion.dietry_rules import DietaryRules


class ProductTransformer:

    # ---------------------------------------------------------

    def transform(
        self,
        data: dict,
    ) -> list[dict]:

        products = data["products"]
        nutrition = data["nutrition"]
        categories = data["categories"]
        brands = data["brands"]

        documents = []

        for product_id, product in products.items():

            nutrition_data = nutrition.get(
                product_id,
                {},
            )

            category = categories.get(
                product["category_id"],
                {},
            )

            brand = brands.get(
                product["brand_id"],
                {},
            )

            document = {

                # ----------------------------------------
                # Identity
                # ----------------------------------------

                "product_id": product_id,

                "product_name": product["product_name"],

                # ----------------------------------------
                # Category
                # ----------------------------------------

                "category_id": product["category_id"],

                "category_name": category.get(
                    "category_name"
                ),

                "processing_level": category.get(
                    "processing_level"
                ),

                # ----------------------------------------
                # Brand
                # ----------------------------------------

                "brand_id": product["brand_id"],

                "brand_name": brand.get(
                    "brand_name"
                ),

                "brand_type": brand.get(
                    "brand_type"
                ),

                # ----------------------------------------
                # Availability
                # ----------------------------------------

                "is_organic_available": product[
                    "is_organic_available"
                ],

                # ----------------------------------------
                # Nutrition
                # ----------------------------------------

                **nutrition_data,

            }

            # =====================================================
            # Dietary Classification
            # =====================================================

            document["diabetic_friendly"] = (

                DietaryRules.diabetic_friendly(

                    document

                )

            )

            document["is_vegan"] = (

                DietaryRules.vegan(

                    document

                )

            )

            document["is_gluten_free"] = (

                DietaryRules.gluten_free(

                    document

                )

            )

            # =====================================================
            # Recommendation Features
            # =====================================================

            document["heart_healthy"] = (

                DietaryRules.heart_healthy(

                    document

                )

            )

            document["high_protein"] = (

                DietaryRules.high_protein(

                    document

                )

            )

            document["low_sugar"] = (

                DietaryRules.low_sugar(

                    document

                )

            )

            # =====================================================

            document["search_text"] = (

                self._build_search_text(

                    document

                )

            )

            documents.append(document)

        return documents
        # ---------------------------------------------------------

    def _build_search_text(
        self,
        document: dict,
    ) -> str:

        values = [

            document.get("product_name"),

            document.get("brand_name"),

            document.get("category_name"),

            document.get("processing_level"),

        ]

        #
        # Nutrition values
        #

        nutrition_fields = [

            ("Protein", "protein_g"),

            ("Calories", "calories_100g"),

            ("Fiber", "fiber_g"),

            ("Fat", "fat_g"),

            ("Sugar", "added_sugar_g"),

            ("Sodium", "sodium_mg"),

            ("Potassium", "potassium_mg"),

        ]

        for label, field in nutrition_fields:

            value = document.get(field)

            if value is not None:

                values.append(

                    f"{label} {value}"

                )

        #
        # Product Features
        #

        if document.get("is_organic_available"):

            values.append("Organic")

        if document.get("is_whole_grain"):

            values.append("Whole Grain")

        if document.get("is_refined_grain"):

            values.append("Refined Grain")

        if document.get("deep_fried"):

            values.append("Deep Fried")

        if document.get("has_artificial_additives"):

            values.append("Artificial Additives")

        #
        # Dietary Classification
        #

        if document.get("diabetic_friendly"):

            values.append("Diabetic Friendly")

        if document.get("is_vegan"):

            values.append("Vegan")

        if document.get("is_gluten_free"):

            values.append("Gluten Free")

        #
        # Recommendation Features
        #

        if document.get("heart_healthy"):

            values.append("Heart Healthy")

        if document.get("high_protein"):

            values.append("High Protein")

        if document.get("low_sugar"):

            values.append("Low Sugar")

        #
        # Brand Type
        #

        if document.get("brand_type"):

            values.append(

                document["brand_type"]

            )

        #
        # Category
        #

        if document.get("category_name"):

            values.append(

                document["category_name"]

            )

        #
        # Remove duplicates while
        # preserving order.
        #

        values = list(

            dict.fromkeys(

                str(v)

                for v in values

                if v not in (None, "")

            )

        )

        return " | ".join(values)