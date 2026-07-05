from pprint import pprint

from agents.ingestion.loader import ProductLoader
from agents.ingestion.transformer import ProductTransformer

loader = ProductLoader()

data = loader.load()

transformer = ProductTransformer()

documents = transformer.transform(data)

print(f"Documents : {len(documents)}")

print()

pprint(documents[0])