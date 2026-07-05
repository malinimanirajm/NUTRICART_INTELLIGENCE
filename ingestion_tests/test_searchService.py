from agents.search.service import SearchService

service = SearchService()

state = service.search(
    customer_id="C0001",
    query="show dairy products with protein greater than 10g"
)

print(state.status)
print(state.message)
print(len(state.products))

for product in state.products:
    print(product["product_name"])