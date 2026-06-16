import weaviate

def run_hybrid_search(search_query, alpha=0.5):
    """
    Performs hybrid search combining BM25 (keywords) and Vector (semantic).
    """
    with weaviate.connect_to_local() as client:
        collection = client.collections.get("NutricartUnified")
        
        # Hybrid search performs both keyword and vector search in parallel
        response = collection.query.hybrid(
            query=search_query,
            alpha=alpha,
            limit=10
        )
        
        print(f"\n--- Hybrid Search Results for: '{search_query}' ---")
        for obj in response.objects:
            # We print the data_type to distinguish between grocery and PDF
            d_type = obj.properties.get("data_type", "unknown")
            content = obj.properties.get("content", "")
            print(f"[{d_type.upper()}] {content[:150]}...")

if __name__ == "__main__":
    # Example: Searching for "high protein snacks"
    # BM25 will catch "protein" or "snack" in grocery data
    # Vector search will understand the concept of healthy eating in PDFs
    run_hybrid_search(" customer cs0016 wants high protein snacks with 10g of protein and sugar between 5g to 7g", alpha=0.5)