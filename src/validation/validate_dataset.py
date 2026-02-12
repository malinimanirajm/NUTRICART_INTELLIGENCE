"""
Dataset Validation Script
--------------------------
Production-grade dataset quality gate.
"""

import csv
import json
from pathlib import Path
from datetime import datetime

# ===============================
# PATH SETUP
# ===============================
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "raw"/"q1_2024_v1"
METADATA_DIR = BASE_DIR / "data" / "metadata"
METADATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = METADATA_DIR / "q1_2024_v1_validation.json"

REQUIRED_FILES = [
    "customers.csv",
    "categories.csv",
    "brands.csv",
    "products.csv",
    "nutrition.csv",
    "transactions.csv",
    "transaction_items.csv",
    "DATASET_METADATA.json"
]

# ===============================
# HELPER FUNCTIONS
# ===============================

def file_exists(file_path: Path) -> bool:
    return file_path.exists() and file_path.is_file()


def count_rows(csv_path: Path) -> int:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        return sum(1 for _ in reader)


def load_column_set(csv_path: Path, column_name: str) -> set:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row[column_name] for row in reader}


def check_unique(csv_path: Path, column: str) -> bool:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        values = [row[column] for row in reader]
        return len(values) == len(set(values))


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
# 1️⃣ File Existence
# -------------------------------

missing_files = []
for file_name in REQUIRED_FILES:
    if not file_exists(DATA_DIR / file_name):
        missing_files.append(file_name)

validation_results["checks"]["required_files_present"] = {
    "passed": len(missing_files) == 0,
    "missing_files": missing_files
}

if missing_files:
    validation_results["status"] = "FAILED"

# -------------------------------
# 2️⃣ Row Count Validation
# -------------------------------

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
# 3️⃣ Primary Key Uniqueness
# -------------------------------

validation_results["checks"]["primary_keys_unique"] = {
    "customers_unique": check_unique(DATA_DIR / "customers.csv", "customer_id"),
    "products_unique": check_unique(DATA_DIR / "products.csv", "product_id"),
    "transactions_unique": check_unique(DATA_DIR / "transactions.csv", "transaction_id")
}

if not all(validation_results["checks"]["primary_keys_unique"].values()):
    validation_results["status"] = "FAILED"

# -------------------------------
# 4️⃣ Schema Validation (Products)
# -------------------------------

EXPECTED_PRODUCT_COLUMNS = {
    "product_id",
    "product_name",
    "category_id",
    "brand_id",
    "is_organic_available"
}

with open(DATA_DIR / "products.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    actual = set(reader.fieldnames)

validation_results["checks"]["product_schema_valid"] = {
    "passed": actual == EXPECTED_PRODUCT_COLUMNS,
    "missing": list(EXPECTED_PRODUCT_COLUMNS - actual),
    "extra": list(actual - EXPECTED_PRODUCT_COLUMNS)
}

if actual != EXPECTED_PRODUCT_COLUMNS:
    validation_results["status"] = "FAILED"

# -------------------------------
# 5️⃣ Foreign Key Integrity
# -------------------------------

products = load_column_set(DATA_DIR / "products.csv", "product_id")
transactions = load_column_set(DATA_DIR / "transactions.csv", "transaction_id")

item_product_ids = load_column_set(DATA_DIR / "transaction_items.csv", "product_id")
item_transaction_ids = load_column_set(DATA_DIR / "transaction_items.csv", "transaction_id")

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
# 6️⃣ Nutrition Sanity Checks
# -------------------------------

nutrition_errors = []

with open(DATA_DIR / "nutrition.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        calories = int(row["calories_100g"])
        protein = float(row["protein_g"])
        fiber = float(row["fiber_g"])
        sugar = float(row["added_sugar_g"])

        if calories <= 0 or calories > 1000:
            nutrition_errors.append(f"{row['product_id']} invalid calories")

        if protein < 0 or protein > 100:
            nutrition_errors.append(f"{row['product_id']} invalid protein")

        if fiber < 0 or fiber > 100:
            nutrition_errors.append(f"{row['product_id']} invalid fiber")

        if sugar < 0:
            nutrition_errors.append(f"{row['product_id']} invalid sugar")

validation_results["checks"]["nutrition_sanity"] = {
    "passed": len(nutrition_errors) == 0,
    "errors": nutrition_errors[:10]
}

if nutrition_errors:
    validation_results["status"] = "FAILED"

# -------------------------------
# 7️⃣ Dataset Freeze Check
# -------------------------------
DATA_DIR = BASE_DIR /"data" / "raw" / "q1_2024_v1"

with open(DATA_DIR /"DATASET_METADATA.json", encoding="utf-8") as f:
    dataset_metadata = json.load(f)

validation_results["checks"]["dataset_freeze"] = {
    "frozen": dataset_metadata.get("frozen", False),
    "seed_present": "random_seed" in dataset_metadata
}

if not dataset_metadata.get("frozen", False):
    validation_results["status"] = "TRUE"

# ===============================
# WRITE REPORT
# ===============================
print("RUNNING FILE:", __file__)


with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(validation_results, f, indent=2)

print("✅ Dataset validation completed")
print(f"📄 Validation report written to: {OUTPUT_PATH}")
print(f"📊 Final Status: {validation_results['status']}")
