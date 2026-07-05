from pprint import pprint

from agents.ingestion.loader import ProductLoader

loader = ProductLoader()

data = loader.load()

print(f"Products   : {len(data['products'])}")
print(f"Nutrition  : {len(data['nutrition'])}")
print(f"Brands     : {len(data['brands'])}")
print(f"Categories : {len(data['categories'])}")

print("\nFirst Product")
pprint(next(iter(data["products"].values())))