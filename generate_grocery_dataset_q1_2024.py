import csv
import random
from datetime import datetime, timedelta, time
import os
import json
from src.config import *
import numpy as np



START_DATE = datetime.strptime(START_DATE, "%Y-%m-%d").date()
END_DATE = datetime.strptime(END_DATE, "%Y-%m-%d").date()



# ===============================
# FREEZE RANDOMNESS
# ===============================

random.seed(SEED)
np.random.seed(SEED)
OUTPUT_DIR = f"{BASE_DATA_DIR}/{DATA_VERSION}"


# ===============================
# CREATE VERSIONED OUTPUT DIR
# ===============================

OUTPUT_DIR = f"{BASE_DATA_DIR}/{DATA_VERSION}"

if os.path.exists(OUTPUT_DIR):
    raise RuntimeError(
        f"Dataset version '{DATA_VERSION}' already exists. "
        "Increment DATA_VERSION to create a new frozen snapshot."
    )

os.makedirs(OUTPUT_DIR)



# =====================
# MASTER DATA
# =====================
CITIES = [
    ("Bangalore", "Karnataka"), ("Chennai", "Tamil Nadu"),
    ("Hyderabad", "Telangana"), ("Mumbai", "Maharashtra"),
    ("Delhi", "Delhi"), ("Pune", "Maharashtra"),
    ("Kochi", "Kerala"), ("Coimbatore", "Tamil Nadu")
]

CATEGORIES = [
    (1, "Staples", "Processed"),
    (2, "Produce", "Unprocessed"),
    (3, "Snacks", "Ultra-Processed"),
    (4, "Bakery", "Processed"),
    (5, "Beverages", "Ultra-Processed"),
    (6, "Dairy", "Processed")
]

BRANDS = [
    (1, "FreshFarm", "Organic-first"),
    (2, "PureHarvest", "Organic-first"),
    (3, "GreenLeaf", "Organic-first"),
    (4, "NatureNest", "Organic-first"),
    (5, "DailyChoice", "Private Label"),
    (6, "ValueMart", "Private Label"),
    (7, "HomeBest", "Private Label"),
    (8, "QuickBuy", "Private Label"),
    (9, "TasteCo", "National"),
    (10, "Snackify", "National"),
    (11, "CrunchyBite", "National"),
    (12, "BakeHouse", "National"),
    (13, "CoolSip", "National"),
    (14, "DairyPure", "National"),
    (15, "UrbanEats", "Local")
]

# =====================
# NUTRITION TEMPLATES
# =====================
NUTRITION_TEMPLATES = {
    "Produce": {
        "calories": (30, 80), "carbs": (5, 15), "fiber": (2, 6),
        "protein": (0, 3), "fat": (0, 2), "healthy_fat": (0, 1),
        "sat_fat": (0, 0), "added_sugar": (0, 0),
        "sodium": (5, 30), "potassium": (200, 400),
        "whole_grain": False, "refined_grain": False,
        "additives": False, "deep_fried": False
    },
    "Staples": {
        "calories": (200, 350), "carbs": (30, 60), "fiber": (3, 10),
        "protein": (6, 12), "fat": (1, 8), "healthy_fat": (1, 4),
        "sat_fat": (0, 2), "added_sugar": (0, 3),
        "sodium": (50, 300), "potassium": (100, 300),
        "whole_grain": None, "refined_grain": None,
        "additives": 0.2, "deep_fried": False
    },
    "Dairy": {
        "calories": (120, 220), "carbs": (4, 12), "fiber": (0, 0),
        "protein": (8, 18), "fat": (4, 12), "healthy_fat": (1, 4),
        "sat_fat": (3, 7), "added_sugar": (0, 6),
        "sodium": (80, 200), "potassium": (150, 250),
        "whole_grain": False, "refined_grain": False,
        "additives": 0.3, "deep_fried": False
    },
    "Snacks": {
        "calories": (450, 550), "carbs": (40, 70), "fiber": (1, 4),
        "protein": (3, 7), "fat": (20, 35), "healthy_fat": (1, 5),
        "sat_fat": (8, 15), "added_sugar": (15, 30),
        "sodium": (300, 900), "potassium": (50, 150),
        "whole_grain": 0.2, "refined_grain": True,
        "additives": True, "deep_fried": 0.6
    },
    "Bakery": "Snacks",
    "Beverages": {
        "calories": (40, 120), "carbs": (5, 30), "fiber": (0, 0),
        "protein": (0, 2), "fat": (0, 3), "healthy_fat": (0, 0),
        "sat_fat": (0, 0), "added_sugar": (5, 25),
        "sodium": (10, 100), "potassium": (20, 80),
        "whole_grain": False, "refined_grain": False,
        "additives": 0.7, "deep_fried": False
    }
}

def sample_value(x):
    if isinstance(x, tuple):
        return random.randint(*x)
    if isinstance(x, float):
        return random.random() < x
    if x is None:
        return random.random() < 0.5
    return x

def sample_nutrition(category):
    tpl = NUTRITION_TEMPLATES[category]
    if tpl == "Snacks":
        tpl = NUTRITION_TEMPLATES["Snacks"]

    return {k: sample_value(v) for k, v in tpl.items()}

# =====================
# CUSTOMERS
# =====================
customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    city, state = random.choice(CITIES)
    customers.append({
        "customer_id": f"C{i:04d}",
        "city": city,
        "state": state,
        "household_size": random.randint(1, 5),
        "organic_preference": random.choices(
            ["Low", "Medium", "High"], [0.4, 0.35, 0.25]
        )[0]
    })

with open(f"{OUTPUT_DIR}/customers.csv", "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["customer_id", "city", "state",
                    "household_size", "organic_preference"]
    )
    writer.writeheader()
    writer.writerows(customers)

# =====================
# CATEGORIES & BRANDS
# =====================
with open(f"{OUTPUT_DIR}/categories.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["category_id", "category_name", "processing_level"])
    writer.writerows(CATEGORIES)

with open(f"{OUTPUT_DIR}/brands.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["brand_id", "brand_name", "brand_type"])
    writer.writerows(BRANDS)

# =====================
# PRODUCTS + NUTRITION
# =====================
products, nutrition = [], []
pid = 1

for cid, cname, _ in CATEGORIES:
    for i in range(PRODUCTS_PER_CATEGORY):
        brand = random.choice(BRANDS)
        product_id = f"P{pid:05d}"

        products.append([
            product_id,
            f"{brand[1]}_{cname}_Item_{i+1}",
            cid,
            brand[0],
            brand[2] == "Organic-first"
        ])

        n = sample_nutrition(cname)
        nutrition.append([
            product_id,
            n["calories"], n["carbs"], n["fiber"], n["protein"],
            n["fat"], n["healthy_fat"], n["sat_fat"], n["added_sugar"],
            n["sodium"], n["potassium"],
            n["whole_grain"], n["refined_grain"],
            n["additives"], n["deep_fried"]
        ])

        pid += 1

with open(f"{OUTPUT_DIR}/products.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "product_id", "product_name",
        "category_id", "brand_id",
        "is_organic_available"
    ])
    writer.writerows(products)

with open(f"{OUTPUT_DIR}/nutrition.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "product_id", "calories_100g", "carbs_g", "fiber_g",
        "protein_g", "fat_g", "healthy_fat_g",
        "saturated_fat_g", "added_sugar_g",
        "sodium_mg", "potassium_mg",
        "is_whole_grain", "is_refined_grain",
        "has_artificial_additives", "deep_fried"
    ])
    writer.writerows(nutrition)

# =====================
# TRANSACTIONS (1–5 / WEEK)
# =====================
txn_f = open(f"{OUTPUT_DIR}/transactions.csv", "w", newline="")
item_f = open(f"{OUTPUT_DIR}/transaction_items.csv", "w", newline="")

txn_w = csv.writer(txn_f)
item_w = csv.writer(item_f)

txn_w.writerow(["transaction_id", "customer_id",
                "transaction_date", "transaction_time"])
item_w.writerow(["item_id", "transaction_id",
                 "product_id", "quantity", "is_organic_purchased"])

txn_id, item_id = 1, 1
current = START_DATE

while current <= END_DATE:
    week_days = [current + timedelta(days=i)
                 for i in range(min(7, (END_DATE - current).days + 1))]

    for cust in customers:
        for d in random.sample(week_days, random.randint(1, 5)):
            txn = f"T{txn_id:06d}"
            t_time = (
                time(random.randint(7, 10), random.choice([0, 30]))
                if random.random() < 0.4
                else time(random.randint(17, 21), random.choice([0, 30]))
            )

            txn_w.writerow([
                txn, cust["customer_id"],
                d.strftime("%Y-%m-%d"), t_time.strftime("%H:%M:%S")
            ])

            for _ in range(random.randint(3, 7)):
                p = random.choice(products)
                item_w.writerow([
                    f"I{item_id:07d}", txn, p[0],
                    random.randint(1, cust["household_size"]),
                    p[4] and cust["organic_preference"] == "High"
                ])
                item_id += 1

            txn_id += 1

    current += timedelta(days=7)

txn_f.close()
item_f.close()

print("✅ Optimized Q2-2024 grocery nutrition dataset generated.")

# ===============================
# DATASET METADATA (FREEZE RECORD)
# ===============================

metadata = {
    "dataset_version": DATA_VERSION,
    "generated_at_utc": datetime.utcnow().isoformat(),
    "config": {
        "seed": SEED,
        "num_customers": NUM_CUSTOMERS,
        "min_purchases_per_week": MIN_PURCHASES_PER_WEEK,
        "max_purchases_per_week": MAX_PURCHASES_PER_WEEK,
        "start_date": START_DATE.strftime("%Y-%m-%d"),
        "end_date": END_DATE.strftime("%Y-%m-%d"),
        "products_per_category": PRODUCTS_PER_CATEGORY
    },
    "schema_version": "v1",
    "frozen": True
}


with open(f"{OUTPUT_DIR}/_METADATA.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

