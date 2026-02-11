from weaviate import connect_to_local

client = connect_to_local(skip_init_checks=True)

try:
    collection = client.collections.get("Product")

    results = collection.query.bm25(
        query="protein snack",
        limit=5
    )

    if not results.objects:
        print("No results found.")
    else:
        print("Top results:")
        for obj in results.objects:
            print("-", obj.properties["product_name"])

finally:
    client.close()

