"""
Search Service Integration Test

Tests the complete pipeline:

Query
    ↓
Normalizer
    ↓
Parser
    ↓
Validator
    ↓
Filter Builder
    ↓
Weaviate
    ↓
Search Results
"""

from dataclasses import asdict, is_dataclass
from pprint import pprint

from agents.search.service import SearchService


def print_result(state):

    print("=" * 100)

    print("Query")
    print(state.query)

    print("\nStatus")
    print(state.status)

    print("\nMessage")
    print(state.message)

    print("\nFilters")

    if state.filters is None:

        print("None")

    elif is_dataclass(state.filters):

        pprint(asdict(state.filters))

    elif hasattr(state.filters, "__dict__"):

        pprint(vars(state.filters))

    else:

        pprint(state.filters)

    products = state.products or []

    print("\nProducts Returned")
    print(len(products))

    for product in products:

        score = product.get("score")

        if isinstance(score, (int, float)):
            score = round(score, 3)
        else:
            score = "-"

        print(
            f"{product.get('product_name','-'):<35}"
            f" Category={product.get('category_name','-'):<12}"
            f" Brand={product.get('brand_name','-'):<15}"
            f" Protein={product.get('protein_g','-'):>5}"
            f" Sugar={product.get('added_sugar_g','-'):>5}"
            f" Calories={product.get('calories_100g','-'):>6}"
            f" Score={score}"
        )

    print("=" * 100)
    print()


def main():

    service = SearchService()

    test_queries = [

        # --------------------------------------------------
        # Category
        # --------------------------------------------------

        "show beverages",
        "show snacks",
        "show produce",

        # --------------------------------------------------
        # Brand
        # --------------------------------------------------

        "show NatureNest products",
        "show FreshFarm products",

        # --------------------------------------------------
        # Protein
        # --------------------------------------------------

        "protein greater than 15g",
        "protein less than 5g",
        "protein between 10 and 20g",

        # --------------------------------------------------
        # Sugar
        # --------------------------------------------------

        "sugar less than 5g",
        "sugar greater than 10g",

        # --------------------------------------------------
        # Calories
        # --------------------------------------------------

        "calories below 100",
        "calories between 100 and 200",

        # --------------------------------------------------
        # Multiple Filters
        # --------------------------------------------------

        "show dairy with protein greater than 10g",
        "show dairy with protein greater than 10g and sugar less than 5g",

        # --------------------------------------------------
        # Preferences
        # --------------------------------------------------

        "show diabetic products",
        "show vegan products",
        "show organic dairy",

        # --------------------------------------------------
        # Natural Language
        # --------------------------------------------------

        "I need healthy dairy products",
        "Give me something high protein",

        # --------------------------------------------------
        # Typo Handling
        # --------------------------------------------------

        "bevrages",
        "protien greater than 20g",
        "suger below 5",

        # --------------------------------------------------
        # Empty
        # --------------------------------------------------

        "",
        " ",

        # --------------------------------------------------
        # Unknown
        # --------------------------------------------------

        "abcdef",
        "show xyz products"

    ]

    for query in test_queries:

        try:

            state = service.search(

                customer_id="C0001",

                query=query,

                top_k=10,

            )

            print_result(state)

        except Exception as ex:

            print("=" * 100)
            print(f"FAILED QUERY : {query}")
            print(ex)
            print("=" * 100)


if __name__ == "__main__":

    main()