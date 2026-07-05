from agents.ingestion.loader import ProductLoader
from agents.ingestion.transformer import ProductTransformer
from agents.ingestion.validator import ProductValidator

loader = ProductLoader()
transformer = ProductTransformer()
validator = ProductValidator()

documents = transformer.transform(loader.load())

valid = 0
invalid = 0

for document in documents:

    result = validator.validate(document)

    if result.valid:
        valid += 1
    else:
        invalid += 1
        print(document["product_id"], result.errors)

print()
print("Valid   :", valid)
print("Invalid :", invalid)