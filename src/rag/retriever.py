import weaviate
import config

def search_products(query, limit=10):
    client = weaviate.connect_to_local(host="127.0.0.1", port=8080)
    collection = client.collections.get(config.COLLECTION_NAME)
    
    results = collection.query.near_text(query=query, limit=limit)
    
    context_list = []
    for obj in results.objects:
        context_list.append(obj.properties.get('text'))
    
    client.close()
    return "\n\n".join(context_list)