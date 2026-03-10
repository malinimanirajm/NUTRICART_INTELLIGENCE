import weaviate
from weaviate.classes.query import Filter
import src.rag.config as config

def search_products(query, max_sugar=None, limit=10):
    client = weaviate.connect_to_local(host="127.0.0.1", port=8080)
    collection = client.collections.get(config.COLLECTION_NAME)
    
    # Apply a hard numerical filter
    results = collection.query.near_text(
        query=query,
        filters=Filter.by_property("added_sugar").less_than(5.0), # The DB does the math!
        limit=limit
    )
    
    context_list = []
    for obj in results.objects:
        # It's helpful to include the actual sugar value in the context 
        # so the LLM can see the "proof"
        props = obj.properties
        text_data = props.get('text', '')
        sugar_val = props.get('added_sugar', 'N/A')
        context_list.append(f"{text_data} (Sugar: {sugar_val}g)")
    
    client.close()
    return "\n\n".join(context_list)