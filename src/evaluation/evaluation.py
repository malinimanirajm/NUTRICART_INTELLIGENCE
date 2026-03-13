from langsmith import evaluate
from src.rag.parser import extract_normalized_filters

def check_math_accuracy(run, example):
    predicted = run.outputs # This comes from extract_normalized_filters
    expected = example.outputs.get("expected")
    return {"score": 1 if predicted == expected else 0, "key": "unit_normalization_score"}

# Run the Experiment
print("Starting Evaluation...")
evaluate(
    extract_normalized_filters,
    data="NutriCart_Unit_Normalization_v1",
    evaluators=[check_math_accuracy],
    experiment_prefix="mg-to-g-normalization-test"
)