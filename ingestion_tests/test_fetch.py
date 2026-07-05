import weaviate

from config.search_config import COLLECTION_NAME

client = weaviate.connect_to_local()

collection = client.collections.get(COLLECTION_NAME)

response = collection.query.fetch_objects(limit=5)

print(f"Objects Returned : {len(response.objects)}")

for obj in response.objects:
    print("-" * 80)
    print(obj.properties)

client.close()