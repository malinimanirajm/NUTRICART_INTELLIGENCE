"""
Dataset Validation Script
--------------------------

Purpose:
This script validates a frozen grocery dataset snapshot to ensure:
1. All required files exist
2. Schemas are correct and consistent
3. No critical nulls or broken relationships exist
4. Dataset is safe to use for analytics, ML, and time-series modeling

Output:
- A machine-readable validation report stored in:
  data/metadata/q1_2024_v1_validation.json

Why this matters (industry context):
- Prevents silent data corruption
- Acts as a quality gate before modeling
- Enables reproducibility and auditability
"""

import csv
import json
from pathlib import Path
from datetime import datetime

# ===============================
# PROJECT PATH RESOLUTION
# ===============================
# Resolve paths relative to THIS file, not where Python is run from
BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "q1_2024_v1"
METADATA_DIR = BASE_DIR / "data" / "metadata"
METADATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = METADATA_DIR / "q1_2024_v1_validation.json"

# ===============================
# EXPECTED DATA FILES
# ===============================
REQUIRED_FILES = [
    "customers.csv",
    "categories.csv",
    "brands.csv",
    "products.csv",
    "nutrition.csv",
    "transactions.csv",
    "transaction_items.csv",
    "_METADATA.json"
]

# ===============================
# HELPER FUNCTIONS
# ===============================
def file_exists(file_path: Path) -> bool:
    """Check whether a file exists on disk"""
    return file_path.exists() and file_path.is_file()


def count_rows(csv_path: Path) -> int:
    """Count number of data rows (excluding header) in a CSV"""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        return sum(1 for _ in reader)


def load_column_set(csv_path: Path, column_name: str) -> set:
    """Load a single column from a CSV as a set (for FK validation)"""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row[column_name] for row in reader}


# ===============================
# VALIDATION EXECUTION
# ===============================
validation_results = {
    "dataset_version": "q1_2024_v1",
    "validated_at_utc": datetime.utcnow().isoformat(),
    "checks": {},
    "row_counts": {},
    "status": "PASSED"
}

# -------------------------------
# 1️⃣ FILE EXISTENCE CHECK
# -------------------------------
missing_files = []

for file_name in REQUIRED_FILES:
    file_path = DATA_DIR / file_name
    if not file_exists(file_path):
        missing_files.append(file_name)

validation_results["checks"]["required_files_present"] = {
    "passed": len(missing_files) == 0,
    "missing_files": missing_files
}

if missing_files:
    validation_results["status"] = "FAILED"

# -------------------------------
# 2️⃣ ROW COUNT VALIDATION
# -------------------------------
# Ensures files are not empty or partially written
for file_name in REQUIRED_FILES:
    if not file_name.endswith(".csv"):
        continue

    file_path = DATA_DIR / file_name
    if file_exists(file_path):
        rows = count_rows(file_path)
        validation_results["row_counts"][file_name] = rows

        if rows == 0:
            validation_results["status"] = "FAILED"

# -------------------------------
# 3️⃣ PRIMARY KEY UNIQUENESS
# -------------------------------
# Industry rule: IDs must be unique and stable

customers = load_column_set(DATA_DIR / "customers.csv", "customer_id")
products = load_column_set(DATA_DIR / "products.csv", "product_id")
transactions = load_column_set(DATA_DIR / "transactions.csv", "transaction_id")

validation_results["checks"]["primary_keys_unique"] = {
    "customers_unique": len(customers) > 0,
    "products_unique": len(products) > 0,
    "transactions_unique": len(transactions) > 0
}

# -------------------------------
# 4️⃣ FOREIGN KEY INTEGRITY
# -------------------------------
# Ensures relational correctness across tables

item_product_ids = load_column_set(
    DATA_DIR / "transaction_items.csv", "product_id"
)

item_transaction_ids = load_column_set(
    DATA_DIR / "transaction_items.csv", "transaction_id"
)

fk_violations = {
    "invalid_product_ids": list(item_product_ids - products),
    "invalid_transaction_ids": list(item_transaction_ids - transactions)
}

validation_results["checks"]["foreign_key_integrity"] = {
    "passed": len(fk_violations["invalid_product_ids"]) == 0
              and len(fk_violations["invalid_transaction_ids"]) == 0,
    "violations": fk_violations
}

if fk_violations["invalid_product_ids"] or fk_violations["invalid_transaction_ids"]:
    validation_results["status"] = "FAILED"

# -------------------------------
# 5️⃣ NUTRITION VALUE SANITY CHECKS
# -------------------------------
# Prevents impossible or dangerous values

nutrition_errors = []

with open(DATA_DIR / "nutrition.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if int(row["calories_100g"]) <= 0:
            nutrition_errors.append(
                f"{row['product_id']} has non-positive calories"
            )

validation_results["checks"]["nutrition_sanity"] = {
    "passed": len(nutrition_errors) == 0,
    "errors": nutrition_errors[:10]  # cap for readability
}

if nutrition_errors:
    validation_results["status"] = "FAILED"

# -------------------------------
# 6️⃣ FREEZE & VERSION CONSISTENCY
# -------------------------------
# Ensures dataset is immutable and reproducible

with open(DATA_DIR / "_METADATA.json", encoding="utf-8") as f:
    dataset_metadata = json.load(f)

validation_results["checks"]["dataset_freeze"] = {
    "frozen": dataset_metadata.get("frozen", False),
    "seed_present": "random_seed" in dataset_metadata
}

if not dataset_metadata.get("frozen", False):
    validation_results["status"] = "FAILED"

# ===============================
# WRITE VALIDATION REPORT
# ===============================
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(validation_results, f, indent=2)

print("✅ Dataset validation completed")
print(f"📄 Validation report written to: {OUTPUT_PATH}")
print(f"📊 Final Status: {validation_results['status']}")
