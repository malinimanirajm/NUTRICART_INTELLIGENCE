from agents.ingestion.loader import ProductLoader
from agents.ingestion.transformer import ProductTransformer
from agents.ingestion.weaviate_writer import WeaviateWriter

loader = ProductLoader()
transformer = ProductTransformer()

documents = transformer.transform(loader.load())

writer = WeaviateWriter()

print("Uploading one product...")

count = writer.write([documents[0]])

writer.close()

print(f"Inserted : {count}")