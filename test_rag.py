import weaviate
# You need this line to access query.Filter and query.hybrid
import weaviate.classes.query as query

def find_healthy_snacks(min_protein, max_sugar):
    with weaviate.connect_to_local() as client:
        collection = client.collections.get("NutricartUnified")
        
        # Apply strict mathematical filters
        filters = (
            query.Filter.by_property("protein_g").greater_or_equal(min_protein) &
            query.Filter.by_property("added_sugar_g").less_or_equal(max_sugar)
        )
        
        response = collection.query.hybrid(
            query="snacks",
            filters=filters,
            limit=2
        )
        
        print(f"\n--- Results: Snacks with >= {min_protein}g protein & <= {max_sugar}g sugar ---")
        for obj in response.objects:
            print(f"Product: {obj.properties['content']} | Protein: {obj.properties.get('protein_g')}g | Sugar: {obj.properties.get('added_sugar_g')}g")

# Run this instead of your general search
find_healthy_snacks(min_protein=10, max_sugar=5)