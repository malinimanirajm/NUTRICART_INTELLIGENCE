from agents.search.service import SearchService

service = SearchService()

test_cases = [

    "show beverages",

    "show snacks",

    "show dairy",

    "show beverages with more than 10g protein",

    "show beverages with less than 5g sugar",

    "show products with protein greater than 15g",

    "show products with sugar less than 3g",

    "show dairy with protein greater than 10g and sugar less than 5g",

    "show beverages between 100 and 200 calories",

    "show diabetic snacks",

    "show vegan products",

    "show organic dairy"

]

for query in test_cases:

    print("=" * 100)
    print("Query :", query)
    print("=" * 100)

    result = service.search(

        customer_id="C101",

        query=query,

        top_k=5

    )

    print("Status :", result.status)
    print("Filters:", result.filters)

    products = result.products

    print(f"Products Returned : {len(products)}")

    print()

    for i, p in enumerate(products, start=1):

        print(f"Product {i}")

        print(f"Brand      : {p.get('brand_name')}")
        print(f"Category   : {p.get('category_name')}")
        print(f"Protein    : {p.get('protein_g')}")
        print(f"Sugar      : {p.get('added_sugar_g')}")
        print(f"Calories   : {p.get('calories_100g')}")
        print(f"Score      : {p.get('score')}")

        # Validation
        valid = True

        f = result.filters

        if f.min_protein is not None:
            valid &= p.get("protein_g", 0) >= f.min_protein

        if f.max_protein is not None:
            valid &= p.get("protein_g", 0) <= f.max_protein

        if f.min_sugar is not None:
            valid &= p.get("added_sugar_g", 0) >= f.min_sugar

        if f.max_sugar is not None:
            valid &= p.get("added_sugar_g", 0) <= f.max_sugar

        if f.min_calories is not None:
            valid &= p.get("calories_100g", 0) >= f.min_calories

        if f.max_calories is not None:
            valid &= p.get("calories_100g", 0) <= f.max_calories

        print("Matches Filters :", valid)

        print("-" * 60)