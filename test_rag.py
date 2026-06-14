import weaviate
import weaviate.classes.query as query

def run_test_query(query_text, data_type=None):
    print(f"\n--- Testing Query: '{query_text}' ---")
    
    with weaviate.connect_to_local() as client:
        collection = client.collections.get("NutricartUnified")
        
        # Define filter if we only want one type of data
        filters = None
        if data_type:
            filters = query.Filter.by_property("data_type").equal(data_type)
        
        # Perform Hybrid Search
        response = collection.query.hybrid(
            query=query_text,
            alpha=0.5,
            limit=3,
            filters=filters
        )
        
        for i, obj in enumerate(response.objects):
            print(f"\nResult {i+1}:")
            print(f"Type: {obj.properties['data_type']}")
            print(f"Content: {obj.properties['content']}")

if __name__ == "__main__":
    # Test 1: Search everything
    run_test_query("organic food purchase")
    
    # Test 2: Search ONLY transactions
    run_test_query("organic food purchase", data_type="transaction")