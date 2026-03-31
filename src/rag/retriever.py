import weaviate
from weaviate.classes.query import Filter
from src.rag import config

def search_products(query, customer_id=None, max_sugar=None, min_protein=None, max_calories=None, category=None, limit=10):
    client = weaviate.connect_to_local(host=config.WEAVIATE_HOST, port=config.WEAVIATE_PORT)
    collection = client.collections.get(config.COLLECTION_NAME)
    filters = []

    if max_sugar is not None:
        filters.append(Filter.by_property("added_sugar").less_than(max_sugar))
    if min_protein is not None:
        filters.append(Filter.by_property("protein").greater_or_equal(min_protein))
    if max_calories is not None:
        filters.append(Filter.by_property("calories").less_than(max_calories))
    if category:
        filters.append(Filter.by_property("category").equal(category))
    if customer_id:
        filters.append(Filter.by_property("customer_id").equal(customer_id))

    filter_obj = Filter.all_of(filters) if filters else None

    response = collection.query.hybrid(
        query=query,
        filters=filter_obj,
        alpha=0.5,
        limit=limit
    )

    context = []
    for obj in response.objects:
        p = obj.properties
        context.append(f"{p['text']} (Protein: {p['protein']}g, Sugar: {p['added_sugar']}g, Calories: {p['calories']})")

    client.close()
    return "\n\n".join(context)