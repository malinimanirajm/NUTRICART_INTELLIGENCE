import weaviate
import weaviate.classes.config as wvc
from src.rag import config # Adjust to match your existing config port/host setup

# Connect to your running instance
client = weaviate.connect_to_local(host=config.WEAVIATE_HOST, port=config.WEAVIATE_PORT)

try:
    if not client.collections.exists("ArticleChunks"):
        client.collections.create(
            name="ArticleChunks",
            description="Holds parsed text, table markdown data, and image visual logs from PDFs",
            # Ensure this vectorizer matches your current system's embedding standard
            vectorizer_config=wvc.Configure.Vectorizer.text2vec_ollama(
                api_endpoint="http://localhost:11434",
                model="nomic-embed-text" 
            ),
            properties=[
                wvc.Property(name="source_file", data_type=wvc.DataType.TEXT, skip_vectorization=True),
                wvc.Property(name="chunk_type", data_type=wvc.DataType.TEXT, skip_vectorization=True),
                wvc.Property(name="page_number", data_type=wvc.DataType.INT, skip_vectorization=True),
                wvc.Property(name="raw_content", data_type=wvc.DataType.TEXT, skip_vectorization=True), # Markdown table or image path
                wvc.Property(name="summary_or_text", data_type=wvc.DataType.TEXT) # WEAVIATE VECTORIZES ONLY THIS PROPERTY
            ]
        )
        print("✅ 'ArticleChunks' collection created successfully!")
    else:
        print("ℹ️ 'ArticleChunks' collection already exists.")
finally:
    client.close()