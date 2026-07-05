from agents.recommendation.service import RecommendationService


def main():

    service = RecommendationService()

    queries = [

        "show dairy",

        "high protein dairy",

        "organic dairy",

        "low sugar snacks",

        "healthy beverages",

    ]

    for query in queries:

        print("=" * 100)
        print("QUERY :", query)
        print("=" * 100)

        result = service.recommend(

            customer_id="C0001",

            query=query,

            top_k=5,

        )

        print(result.status)

        print(result.message)

        print()

        for recommendation in result.recommendations:

            product = recommendation.product

            print(

                product["product_name"]

            )

            print(

                "Score :",

                recommendation.score,

            )

            print(

                "Reasons:",

                recommendation.reasons,

            )

            print("-" * 60)


if __name__ == "__main__":

    main()