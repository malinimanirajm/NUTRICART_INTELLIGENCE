from weaviate import connect_to_local

client = connect_to_local(skip_init_checks=True)

try:
    collection = client.collections.get("Product")

    result = collection.query.fetch_objects(limit=5)

    print("Fetched objects:", len(result.objects))
    for obj in result.objects:
        print(obj.properties)

finally:
    client.close()
