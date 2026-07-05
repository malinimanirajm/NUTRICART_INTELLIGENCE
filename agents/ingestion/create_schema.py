"""
Create Product Search Schema

Responsibilities
----------------
1. Connect to Weaviate
2. Create product collection
3. Define schema
4. Skip if already exists
"""

from __future__ import annotations

import weaviate
from weaviate.classes.config import (
    Configure,
    DataType,
    Property,
)

from config.search_config import COLLECTION_NAME


class SchemaManager:

    def __init__(self):

        self.client = weaviate.connect_to_local()

    # ---------------------------------------------------------

    def create(self):

        collections = self.client.collections.list_all()

        if COLLECTION_NAME in collections:

            print(f"{COLLECTION_NAME} already exists.")

            return

        self.client.collections.create(

            name=COLLECTION_NAME,

            vectorizer_config=Configure.Vectorizer.none(),

            properties=[

                # -------------------------------
                # Identity
                # -------------------------------

                Property(
                    name="product_id",
                    data_type=DataType.TEXT,
                ),

                Property(
                    name="product_name",
                    data_type=DataType.TEXT,
                ),

                # -------------------------------
                # Category
                # -------------------------------

                Property(
                    name="category_name",
                    data_type=DataType.TEXT,
                ),

                Property(
                    name="processing_level",
                    data_type=DataType.TEXT,
                ),

                # -------------------------------
                # Brand
                # -------------------------------

                Property(
                    name="brand_name",
                    data_type=DataType.TEXT,
                ),

                Property(
                    name="brand_type",
                    data_type=DataType.TEXT,
                ),

                # -------------------------------
                # Nutrition
                # -------------------------------

                Property(
                    name="protein_g",
                    data_type=DataType.NUMBER,
                ),

                Property(
                    name="fat_g",
                    data_type=DataType.NUMBER,
                ),

                Property(
                    name="fiber_g",
                    data_type=DataType.NUMBER,
                ),

                Property(
                    name="carbs_g",
                    data_type=DataType.NUMBER,
                ),

                Property(
                    name="healthy_fat_g",
                    data_type=DataType.NUMBER,
                ),

                Property(
                    name="saturated_fat_g",
                    data_type=DataType.NUMBER,
                ),

                Property(
                    name="added_sugar_g",
                    data_type=DataType.NUMBER,
                ),

                Property(
                    name="sodium_mg",
                    data_type=DataType.NUMBER,
                ),

                Property(
                    name="potassium_mg",
                    data_type=DataType.NUMBER,
                ),

                Property(
                    name="calories_100g",
                    data_type=DataType.NUMBER,
                ),

                # -------------------------------
                # Flags
                # -------------------------------

                Property(
                    name="is_organic_available",
                    data_type=DataType.BOOL,
                ),

                Property(
                    name="is_whole_grain",
                    data_type=DataType.BOOL,
                ),

                Property(
                    name="is_refined_grain",
                    data_type=DataType.BOOL,
                ),

                Property(
                    name="has_artificial_additives",
                    data_type=DataType.BOOL,
                ),

                Property(
                    name="deep_fried",
                    data_type=DataType.BOOL,
                ),

                # -------------------------------
                # Search
                # -------------------------------

                Property(
                    name="search_text",
                    data_type=DataType.TEXT,
                ),
                Property(
                name="is_organic_available",
                data_type=DataType.BOOL,
                ),

                Property(
                name="diabetic_friendly",
                data_type=DataType.BOOL,
                ),

                Property(
                name="is_vegan",
                data_type=DataType.BOOL,
                ),

                Property(
                name="is_gluten_free",
                data_type=DataType.BOOL,
                ),
                Property(
                name="heart_healthy",
                data_type=DataType.BOOL,
                ),

                Property(
                    name="high_protein",
                    data_type=DataType.BOOL,
                ),

                Property(
                    name="low_sugar",
                    data_type=DataType.BOOL,
                ),

            ],

        )

        print(f"{COLLECTION_NAME} created successfully.")

    # ---------------------------------------------------------

    def delete(self):

        collections = self.client.collections.list_all()

        if COLLECTION_NAME in collections:

            self.client.collections.delete(

                COLLECTION_NAME

            )

            print(f"{COLLECTION_NAME} deleted.")

    # ---------------------------------------------------------

    def close(self):

        self.client.close()

    # ---------------------------------------------------------

    def __enter__(self):

        return self

    # ---------------------------------------------------------

    def __exit__(

        self,

        exc_type,

        exc_val,

        exc_tb,

    ):

        self.close()


# -------------------------------------------------------------

def main():

    with SchemaManager() as schema:

        schema.create()


# -------------------------------------------------------------

if __name__ == "__main__":

    main()