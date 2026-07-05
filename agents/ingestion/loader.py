"""
Product Loader

Responsibilities
----------------
1. Load products.csv
2. Load nutrition.csv
3. Load categories.csv
4. Load brands.csv
5. Return datasets

No transformations.
No validation.
No Weaviate.
"""

from __future__ import annotations

import csv
from pathlib import Path


class ProductLoader:

    def __init__(
        self,
        data_dir: str = "data/raw/q1_2024_v1",
    ):

        self.data_dir = Path(data_dir)

    # ---------------------------------------------------------

    def load(self) -> dict:

        return {

            "products": self._load_products(),

            "nutrition": self._load_nutrition(),

            "categories": self._load_categories(),

            "brands": self._load_brands(),

        }

    # ---------------------------------------------------------

    def _load_products(self):

        file_path = self.data_dir / "products.csv"

        products = {}

        with open(
            file_path,
            newline="",
            encoding="utf-8"
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:

                products[row["product_id"]] = {

                    "product_id": row["product_id"],

                    "product_name": row["product_name"],

                    "category_id": int(row["category_id"]),

                    "brand_id": int(row["brand_id"]),

                    "is_organic_available": (
                        row["is_organic_available"].lower()
                        == "true"
                    )

                }

        return products

    # ---------------------------------------------------------

    def _load_nutrition(self):

        file_path = self.data_dir / "nutrition.csv"

        nutrition = {}

        with open(
            file_path,
            newline="",
            encoding="utf-8"
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:

                nutrition[row["product_id"]] = {

                    "calories_100g": float(row["calories_100g"]),

                    "carbs_g": float(row["carbs_g"]),

                    "fiber_g": float(row["fiber_g"]),

                    "protein_g": float(row["protein_g"]),

                    "fat_g": float(row["fat_g"]),

                    "healthy_fat_g": float(row["healthy_fat_g"]),

                    "saturated_fat_g": float(row["saturated_fat_g"]),

                    "added_sugar_g": float(row["added_sugar_g"]),

                    "sodium_mg": float(row["sodium_mg"]),

                    "potassium_mg": float(row["potassium_mg"]),

                    "is_whole_grain": (
                        row["is_whole_grain"].lower() == "true"
                    ),

                    "is_refined_grain": (
                        row["is_refined_grain"].lower() == "true"
                    ),

                    "has_artificial_additives": (
                        row["has_artificial_additives"].lower() == "true"
                    ),

                    "deep_fried": (
                        row["deep_fried"].lower() == "true"
                    )

                }

        return nutrition

    # ---------------------------------------------------------

    def _load_categories(self):

        file_path = self.data_dir / "categories.csv"

        categories = {}

        with open(
            file_path,
            newline="",
            encoding="utf-8"
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:

                categories[int(row["category_id"])] = {

                    "category_name": row["category_name"],

                    "processing_level": row["processing_level"]

                }

        return categories

    # ---------------------------------------------------------

    def _load_brands(self):

        file_path = self.data_dir / "brands.csv"

        brands = {}

        with open(
            file_path,
            newline="",
            encoding="utf-8"
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:

                brands[int(row["brand_id"])] = {

                    "brand_name": row["brand_name"],

                    "brand_type": row["brand_type"]

                }

        return brands

if __name__ == "__main__":

    loader = ProductLoader()

    data = loader.load()

    print(f"Products   : {len(data['products'])}")
    print(f"Nutrition  : {len(data['nutrition'])}")
    print(f"Brands     : {len(data['brands'])}")
    print(f"Categories : {len(data['categories'])}")

    print(next(iter(data["products"].values())))