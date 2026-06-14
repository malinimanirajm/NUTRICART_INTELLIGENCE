import weaviate
import weaviate.classes.query as query
from datetime import datetime

class NutricartAnalytics:
    def __init__(self):
        self.client = weaviate.connect_to_local()
        self.collection = self.client.collections.get("NutricartUnified")

    def search_filtered(self, filters_dict):
        """1. Multi-filter search (Products, Brands, Categories for a Customer)"""
        weaviate_filters = [query.Filter.by_property(k).equal(v) for k, v in filters_dict.items()]
        
        response = self.collection.query.hybrid(
            query="transactions",
            filters=query.Filter.all_of(weaviate_filters),
            limit=50
        )
        return response.objects

    def get_nutrition_timeline(self, customer_id, period="monthly"):
        """2. Nutrition consumption by timeframe"""
        # Logic: Filter by customer_id and date range
        # Note: Ensure your schema has 'transaction_date' as a property
        response = self.collection.query.hybrid(
            query="nutrition",
            filters=query.Filter.by_property("customer_id").equal(customer_id)
        )
        # Add logic here to aggregate protein_g / sugar_g based on date
        return response.objects

    def get_nutrition_insights(self, customer_id):
        """3. Get nutritional facts based on past purchases"""
        results = self.get_nutrition_timeline(customer_id)
        
        total_protein = sum(obj.properties.get('protein_g', 0) for obj in results)
        total_sugar = sum(obj.properties.get('added_sugar_g', 0) for obj in results)
        
        return f"Based on your purchases, you've consumed {total_protein}g protein and {total_sugar}g sugar."

if __name__ == "__main__":
    engine = NutricartAnalytics()
    
    # Example 1: Search by Brand/Category for a specific customer
    filters = {"city": "Bengaluru", "brand_name": "NatureNest"}
    data = engine.search_filtered(filters)
    print(f"Found {len(data)} items.")
    
    # Example 3: Get personal insights
    print(engine.get_nutrition_insights("CUST_001"))