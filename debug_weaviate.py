#!/usr/bin/env python3
"""Debug script to check Weaviate data and filters"""

import weaviate
from weaviate.classes.query import Filter

# Connect to Weaviate
client = weaviate.connect_to_local(host="127.0.0.1", port=8080)

try:
    # Check if collection exists
    if not client.collections.exists("Product"):
        print("❌ Product collection does not exist!")
        print("Run /ingest endpoint to create and populate it.")
    else:
        collection = client.collections.get("Product")
        
        # Count total objects
        all_objects = collection.query.fetch_objects(limit=10000)
        total = len(all_objects.objects)
        print(f"✅ Product collection exists with {total} objects")
        
        if total == 0:
            print("⚠️  Collection is empty! Run /ingest to populate.")
        else:
            # Show first few products
            print("\n📊 First 5 products in database:")
            for i, obj in enumerate(all_objects.objects[:5]):
                props = obj.properties
                print(f"  {i+1}. {props.get('product_name')} - Sugar: {props.get('added_sugar')}g")
            
            # Check sugar distribution
            sugar_values = [obj.properties.get('added_sugar', 0) for obj in all_objects.objects]
            print(f"\n📈 Sugar stats:")
            print(f"  Min sugar: {min(sugar_values)}g")
            print(f"  Max sugar: {max(sugar_values)}g")
            print(f"  Avg sugar: {sum(sugar_values)/len(sugar_values):.2f}g")
            
            # Count products with < 5g sugar
            under_5 = sum(1 for s in sugar_values if s < 5)
            print(f"\n🎯 Products with < 5g sugar: {under_5}")
            
            if under_5 > 0:
                print("\n  Examples of products with < 5g sugar:")
                count = 0
                for obj in all_objects.objects:
                    sugar = obj.properties.get('added_sugar', 0)
                    if sugar < 5:
                        print(f"    - {obj.properties.get('product_name')}: {sugar}g sugar")
                        count += 1
                        if count >= 5:
                            break
            
            # Test the BM25 query with filter
            print("\n🔍 Testing BM25 query with max_sugar < 5 filter:")
            try:
                response = collection.query.bm25(
                    query="snacks",
                    where=Filter.by_property("added_sugar").less_than(5.0),
                    limit=5,
                    return_properties=["product_name", "added_sugar", "protein", "calories"]
                )
                print(f"  ✅ BM25 query returned {len(response.objects)} results")
                for obj in response.objects:
                    props = obj.properties
                    print(f"    - {props.get('product_name')}: {props.get('added_sugar')}g sugar")
            except Exception as e:
                print(f"  ❌ BM25 query failed: {e}")
            
            # Test fetch_objects without filter (should get any 5)
            print("\n🔍 Testing fetch_objects (no filter):")
            response = collection.query.fetch_objects(
                limit=5,
                return_properties=["product_name", "added_sugar", "protein", "calories"]
            )
            print(f"  ✅ Fetch query returned {len(response.objects)} results")
            
finally:
    client.close()
    print("\n✅ Done!")
