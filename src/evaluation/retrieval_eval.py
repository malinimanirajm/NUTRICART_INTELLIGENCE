import json
import os
import weaviate
import sys

# Add src to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag import config

def run_retrieval_eval():
    print("🧪 Running Phase 1: Retrieval Evals...")
    
    # Load test queries
    dataset_path = os.path.join(os.path.dirname(__file__), "dataset/queries.json")
    with open(dataset_path, "r") as f:
        queries = json.load(f)
        
    client = weaviate.connect_to_local(host="127.0.0.1", port=8080)
    collection = client.collections.get(config.COLLECTION_NAME)
    
    for test in queries:
        query = test["query"]
        constraints = test["constraints"]
        
        print(f"\nQuerying: {query}")
        
        # 1. Retrieve
        results = collection.query.near_text(query=query, limit=5)
        
        # 2. Score
        total = len(results.objects)
        passed = 0
        
        for obj in results.objects:
            props = obj.properties
            # This requires the text blob to be parsable or metadata to be stored
            # For simplicity, we check if the LLM *could* find the answer
            
            # Note: For strict Phase 1 evals, it's better to store 
            # nutrition data as numerical properties, not just in the text blob.
            
            print(f" - Found: {props['product_name']}")
            passed += 1 # Placeholder logic - needs actual parser
            
        # 3. Report
        print(f"✅ Retrieved {passed}/{total} candidates for: {query}")
        
    client.close()

if __name__ == "__main__":
    run_retrieval_eval()