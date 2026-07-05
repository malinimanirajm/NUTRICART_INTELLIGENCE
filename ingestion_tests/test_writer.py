from agents.ingestion.loader import ProductLoader
from agents.ingestion.transformer import ProductTransformer
from agents.ingestion.weaviate_writer import WeaviateWriter

loader = ProductLoader()
documents = ProductTransformer().transform(loader.load())

writer = WeaviateWriter()

count = writer.write(documents)

writer.close()

print(f"Inserted : {count}")