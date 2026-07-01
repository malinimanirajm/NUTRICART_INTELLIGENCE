from agents.memory_agent import MemoryAgent

memory = MemoryAgent()

# Create customer
memory.create_customer("C0101")

# Update profile
memory.update_medical_condition(
    customer_id="C0101",
    diabetic=True
)

memory.update_goal(
    customer_id="C0101",
    goal="High Protein Diet"
)

# Save searches
memory.save_search(
    customer_id="C0101",
    query="High Protein Snacks",
    category="Protein"
)

memory.save_search(
    customer_id="C0101",
    query="Low Sugar Cookies",
    category="Diabetic"
)

# Save purchase
memory.save_purchase(
    customer_id="C0101",
    product_name="Quest Protein Bar",
    category="Protein Bars",
    protein=20,
    sugar=1,
    calories=190
)

print("\nPROFILE")
print(memory.get_profile("C0101"))

print("\nSEARCH HISTORY")
for row in memory.get_search_history("C0101"):
    print(row)

print("\nPURCHASE HISTORY")
for row in memory.get_purchase_history("C0101"):
    print(row)