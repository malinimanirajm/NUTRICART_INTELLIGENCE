import csv
import random
from datetime import datetime, timedelta, time
import os

random.seed(42)

# =====================
# CONFIG
# =====================
NUM_CUSTOMERS = 400
START_DATE = datetime(2024, 4, 1)
END_DATE = datetime(2024, 6, 30)
OUTPUT_DIR = "grocery_dataset_q2_2024"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================
# CUSTOMERS
# =====================
cities = [
    ("Bangalore", "Karnataka"),
    ("Chennai", "Tamil Nadu"),
    ("Hyderabad", "Telangana"),
    ("Mumbai", "Maharashtra"),
    ("Delhi", "Delhi"),
    ("Pune", "Maharashtra"),
    ("Kochi", "Kerala"),
    ("Coimbatore", "Tamil Nadu")
]

customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    city, state = random.choice(cities)
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
        fieldnames=[
            "customer_id", "city", "state",
            "household_size", "organic_preference"
        ]
    )
    writer.writeheader()
    writer.writerows(customers)

# =====================
# CATEGORIES
# =====================
categories = [
    (1, "Staples", "Processed"),
    (2, "Produce", "Unprocessed"),
    (3, "Snacks", "Ultra-Processed"),
    (4, "Bakery", "Processed"),
    (5, "Beverages", "Ultra-Processed"),
    (6, "Dairy", "Processed")
]

with open(f"{OUTPUT_DIR}/categories.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["category_id", "category_name", "processing_level"])
    writer.writerows(categories)

# =====================
# BRANDS (15)
# =====================
brands = [
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

with open(f"{OUTPUT_DIR}/brands.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["brand_id", "brand_name", "brand_type"])
    writer.writerows(brands)

# =====================
# PRODUCTS + NUTRITION
# =====================
products = []
nutrition = []
pid = 1
PRODUCTS_PER_CATEGORY = 30

for cid, cname, _ in categories:
    for i in range(PRODUCTS_PER_CATEGORY):
        brand = random.choice(brands)
        product_id = f"P{pid:05d}"
        is_organic_available = brand[2] == "Organic-first"

        products.append([
            product_id,
            f"{brand[1]}_{cname}_Item_{i+1}",
            cid,
            brand[0],
            is_organic_available
        ])

        # Nutrition logic
        if cname == "Produce":
            calories, carbs, sugar, fat, protein = (
                random.randint(30, 80),
                random.randint(5, 15),
                random.randint(2, 8),
                random.randint(0, 2),
                random.randint(0, 3)
            )
        elif cname == "Staples":
            calories, carbs, sugar, fat, protein = (
                random.randint(200, 350),
                random.randint(30, 60),
                random.randint(1, 5),
                random.randint(1, 8),
                random.randint(6, 12)
            )
        elif cname == "Dairy":
            calories, carbs, sugar, fat, protein = (
                random.randint(120, 220),
                random.randint(4, 12),
                random.randint(3, 10),
                random.randint(4, 12),
                random.randint(8, 18)
            )
        elif cname in ["Snacks", "Bakery"]:
            calories, carbs, sugar, fat, protein = (
                random.randint(450, 550),
                random.randint(40, 70),
                random.randint(20, 40),
                random.randint(20, 35),
                random.randint(3, 7)
            )
        else:  # Beverages
            calories, carbs, sugar, fat, protein = (
                random.randint(40, 120),
                random.randint(5, 30),
                random.randint(5, 25),
                random.randint(0, 3),
                random.randint(0, 2)
            )

        nutrition.append([
            product_id, calories, carbs, sugar,
            fat, protein, random.randint(50, 900)
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
        "product_id", "calories_100g", "carbs_g",
        "sugar_g", "fat_g", "protein_g", "sodium_mg"
    ])
    writer.writerows(nutrition)

# =====================
# TRANSACTIONS (1–5 / WEEK)
# =====================
txn_f = open(f"{OUTPUT_DIR}/transactions.csv", "w", newline="")
item_f = open(f"{OUTPUT_DIR}/transaction_items.csv", "w", newline="")

txn_w = csv.writer(txn_f)
item_w = csv.writer(item_f)

txn_w.writerow([
    "transaction_id", "customer_id",
    "transaction_date", "transaction_time"
])
item_w.writerow([
    "item_id", "transaction_id",
    "product_id", "quantity", "is_organic_purchased"
])

txn_id = 1
item_id = 1
current = START_DATE

while current <= END_DATE:
    week_end = min(current + timedelta(days=6), END_DATE)

    for cust in customers:
        weekly_purchases = random.randint(1, 5)
        days = random.sample(
            [(current + timedelta(days=i)) for i in range((week_end - current).days + 1)],
            weekly_purchases
        )

        for d in days:
            t_time = (
                time(random.randint(7, 10), random.choice([0, 30]))
                if random.random() < 0.4
                else time(random.randint(17, 21), random.choice([0, 30]))
            )

            txn = f"T{txn_id:06d}"
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

print("✅ Q2-2024 grocery nutrition dataset generated successfully.")
