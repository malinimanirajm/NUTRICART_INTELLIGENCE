"""
Search Agent Configuration

This file contains only configuration.
No business logic.
"""

# ==========================================================
# Weaviate Collection
# ==========================================================

COLLECTION_NAME = "NutricartUnified"


# ==========================================================
# Search Defaults
# ==========================================================

SEARCH_CONFIG = {

    "default_top_k": 10,

    "default_alpha": 0.5,

    "max_top_k": 100

}


# ==========================================================
# Nutrient Configuration
# ==========================================================

NUTRIENTS = {

    "protein": {

        "db_field": "protein_g",

        "min_filter": "min_protein",

        "max_filter": "max_protein"

    },

    "sugar": {

        "db_field": "added_sugar_g",

        "min_filter": "min_sugar",

        "max_filter": "max_sugar"

    },

    "calories": {

        "db_field": "calories_100g",

        "min_filter": "min_calories",

        "max_filter": "max_calories"

    },

    "fat": {

        "db_field": "fat_g",

        "min_filter": "min_fat",

        "max_filter": "max_fat"

    },

    "fiber": {

        "db_field": "fiber_g",

        "min_filter": "min_fiber",

        "max_filter": "max_fiber"

    },

    "sodium": {

        "db_field": "sodium_mg",

        "min_filter": "min_sodium",

        "max_filter": "max_sodium"

    }

}


# ==========================================================
# Dietary Preferences
# ==========================================================

PREFERENCES = {

    "diabetic": {

        "keywords": [

            "diabetic",

            "diabetes"

        ],

        "attribute": "diabetic"

    },

    "vegan": {

        "keywords": [

            "vegan"

        ],

        "attribute": "vegan"

    },

    "organic": {

        "keywords": [

            "organic"

        ],

        "attribute": "organic"

    },

    "gluten_free": {

        "keywords": [

            "gluten free",

            "gluten-free"

        ],

        "attribute": "gluten_free"

    }

}


# ==========================================================
# Search Strategies
# ==========================================================

SEARCH_STRATEGIES = {

    "semantic": {

        "alpha": 1.0

    },

    "keyword": {

        "alpha": 0.0

    },

    "hybrid": {

        "alpha": 0.5

    }

}