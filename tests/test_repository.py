from agents.search.normalizer import QueryNormalizer

normalizer = QueryNormalizer()

queries = [

    "Show me bevrages",

    "Protien >20g",

    "Coockies with suger <3g",

    "High protein snacks",

    "Low sugar cookies"

]

for q in queries:

    print("=" * 50)

    print("Original :", q)

    print("Normalized :", normalizer.normalize(q))