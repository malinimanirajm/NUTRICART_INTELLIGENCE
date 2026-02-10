import weaviate
import json

client = weaviate.Client(
    url="http://localhost:8080"
)

with open("weaviate/schema/grocery_schema.json") as f:
    schema = json.load(f)

existing = client.schema.get()

for cls in schema["classes"]:
    if not any(c["class"] == cls["class"] for c in existing.get("classes", [])):
        client.schema.create_class(cls)
        print(f"✅ Created class: {cls['class']}")
    else:
        print(f"⚠️ Class already exists: {cls['class']}")
