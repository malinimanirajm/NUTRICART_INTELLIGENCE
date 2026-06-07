import os
import fitz  # PyMuPDF
import weaviate
import weaviate.classes.config as wvc
import requests
import base64

# Connect using your project's configuration setup
try:
    from src.rag import config
    WEAVIATE_HOST = config.WEAVIATE_HOST
    WEAVIATE_PORT = config.WEAVIATE_PORT
except ImportError:
    WEAVIATE_HOST = "localhost"
    WEAVIATE_PORT = 8080

# --- Ollama AI Processing Helpers ---
def summarize_table_layout(markdown_table: str) -> str:
    """Uses llama3.2 to smooth out formatting and build a conversational vector target."""
    prompt = f"Identify the core metrics, columns, and summarize key insights of this table data layout concisely:\n{markdown_table}"
    try:
        res = requests.post("http://localhost:11434/api/generate",
                            json={"model": "llama3.2:3b", "prompt": prompt, "stream": False}, timeout=40)
        return res.json().get("response", "").strip()
    except Exception:
        return "Structured data table layout containing nutritional values."

def describe_chart_image(image_path: str) -> str:
    """Uses the llava vision model to translate a cropped binary graphic into clear text sentences."""
    try:
        with open(image_path, "rb") as f:
            encoded_img = base64.b64encode(f.read()).decode('utf-8')
        prompt = "Identify and describe this chart, plot, or visual graphic from the article page. List axis benchmarks, variables, or takeaways explicitly."
        res = requests.post("http://localhost:11434/api/generate",
                            json={"model": "llava:7b", "prompt": prompt, "images": [encoded_img], "stream": False}, timeout=60)
        return res.json().get("response", "").strip()
    except Exception:
        return "Visual chart graphic attachment from the article."

# --- Main Ingestion Core Router ---
def ingest_entire_folder(folder_path: str, output_images_dir: str):
    # 1. Open Connection to Weaviate
    client = weaviate.connect_to_local(host=WEAVIATE_HOST, port=WEAVIATE_PORT)
    
    try:
        # 2. Assert Schema Existence matching your exact parameters
        if not client.collections.exists("ArticleChunks"):
            print("🚀 Creating 'ArticleChunks' collection schema...")
            client.collections.create(
                name="ArticleChunks",
                description="Holds parsed text, table markdown data, and image visual logs from PDFs using PyMuPDF",
                vectorizer_config=wvc.Configure.Vectorizer.text2vec_ollama(
                    api_endpoint="http://localhost:11434",
                    model="nomic-embed-text" 
                ),
                properties=[
                    wvc.Property(name="source_file", data_type=wvc.DataType.TEXT, skip_vectorization=True),
                    wvc.Property(name="chunk_type", data_type=wvc.DataType.TEXT, skip_vectorization=True),
                    wvc.Property(name="page_number", data_type=wvc.DataType.INT, skip_vectorization=True),
                    wvc.Property(name="raw_content", data_type=wvc.DataType.TEXT, skip_vectorization=True), 
                    wvc.Property(name="summary_or_text", data_type=wvc.DataType.TEXT) 
                ]
            )
            print("✅ Collection created successfully!")
            
        collection = client.collections.get("ArticleChunks")
        
        # 3. Filter for target PDF files
        if not os.path.exists(folder_path):
            print(f"❌ Error: Target directory '{folder_path}' does not exist.")
            return

        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        print(f"📂 Found {len(pdf_files)} PDF articles inside '{folder_path}' to process.")

        # 4. Ingestion Loop
        for filename in pdf_files:
            pdf_path = os.path.join(folder_path, filename)
            print(f"\n📄 Processing Document: {filename}...")
            
            # Isolate an output subfolder for this article's extracted charts
            article_slug = os.path.splitext(filename)[0].replace(" ", "_")
            article_img_dir = os.path.join(output_images_dir, article_slug)
            os.makedirs(article_img_dir, exist_ok=True)
            
            doc = fitz.open(pdf_path)
            
            # Utilize Weaviate v4 High-Performance Dynamic Batcher
            with collection.batch.dynamic() as batch:
                for page_num in range(len(doc)):
                    page_idx = page_num + 1
                    page = doc[page_num]
                    
                    # A. Handle Prose Text Layers
                    text = page.get_text()
                    if text.strip():
                        batch.add_object(properties={
                            "source_file": filename, "chunk_type": "text", "page_number": page_idx,
                            "raw_content": text.strip(), "summary_or_text": text.strip()
                        })

                    # B. Handle Visual Tables via PyMuPDF native extractor
                    tables = page.find_tables()
                    for i, table in enumerate(tables):
                        # Safely drop rows into clean Markdown string formats
                        markdown_table = table.to_pandas().to_markdown()
                        
                        # Let Llama 3.2 smooth out alignment issues for the search index vector
                        summary = summarize_table_layout(markdown_table)
                        
                        batch.add_object(properties={
                            "source_file": filename, "chunk_type": "table", "page_number": page_idx,
                            "raw_content": markdown_table, "summary_or_text": summary
                        })

                    # C. Handle Embedded Images & Infographics
                    images = page.get_images(full=True)
                    for img_idx, img in enumerate(images):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        img_path = os.path.join(article_img_dir, f"page_{page_idx}_img_{img_idx}.png")
                        with open(img_path, "wb") as f:
                            f.write(image_bytes)
                        
                        # Translate binary elements to conversational descriptions via Llava
                        description = describe_chart_image(img_path)
                        
                        batch.add_object(properties={
                            "source_file": filename, "chunk_type": "image", "page_number": page_idx,
                            "raw_content": img_path, "summary_or_text": description
                        })
                        
            print(f"✅ Successfully ingested all layout chunks for: {filename}")
            
    finally:
        client.close()
        print("\n🔌 Weaviate connection securely closed.")

if __name__ == "__main__":
    # Configure your workspace targets here
    INPUT_ARTICLES_FOLDER = "./pdf_ingestion/articles_input"
    EXTRACTED_CHARTS_VAULT = "./pdf_ingestion/extracted_charts"
    
    # Initialize workspace directories if missing
    os.makedirs(INPUT_ARTICLES_FOLDER, exist_ok=True)
    os.makedirs(EXTRACTED_CHARTS_VAULT, exist_ok=True)
    
    print("🚀 Initializing Batch Article Ingestion Engine...")
    ingest_entire_folder(INPUT_ARTICLES_FOLDER, EXTRACTED_CHARTS_VAULT)
    print("\n🏁 Folder processing loop complete.")