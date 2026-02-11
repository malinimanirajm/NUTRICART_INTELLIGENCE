from weaviate import connect_to_local

client = connect_to_local(skip_init_checks=True)

try:
    collection = client.collections.get("Product")
    print("Object count:", collection.aggregate.over_all().total_count)
finally:
    client.close()
