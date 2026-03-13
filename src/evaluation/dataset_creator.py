from langsmith import Client

client = Client()
dataset_name = "NutriCart_Unit_Normalization_v1"

# Ground Truth for testing the mg -> g logic
examples = [
    ("Find snacks with 500mg sodium", {"max_sodium": 0.5}),
    ("Snack under 5g sugar and 250mg sodium", {"max_sugar": 5.0, "max_sodium": 0.25}),
    ("Protein > 10g and fiber > 5g", {"min_protein": 10.0, "min_fiber": 5.0})
]

if not client.has_dataset(dataset_name=dataset_name):
    dataset = client.create_dataset(dataset_name)
    for q, a in examples:
        client.create_example(
            inputs={"question": q}, 
            outputs={"expected": a}, 
            dataset_id=dataset.id
        )
    print(f"✅ Successfully created LangSmith Dataset: {dataset_name}")