"""
agents/supervisor/router.py
"""

from agents.search.service import SearchService
from memory.memory_service.memory_service import MemoryService
from agents.recommendation.service import RecommendationService
from agents.nutrition.service import NutritionService
from agents.order.service import OrderService


class Router:

    def __init__(self):

        self.search = SearchService()

        self.memory = MemoryService()

        self.recommendation = RecommendationService()

        self.nutrition = NutritionService()

        self.order = OrderService()

    # -----------------------------------------------------

    def execute(
        self,
        customer_id,
        query,
        agents,
    ):

        results = {}

        if "Search" in agents:

            results["search"] = self.search.search(
                customer_id,
                query,
            )

        if "Recommendation" in agents:

            results["recommendation"] = (
                self.recommendation.recommend(
                    customer_id,
                    query,
                )
            )

        if "Nutrition" in agents:

            results["nutrition"] = (
                self.nutrition.monthly_summary(
                    customer_id
                )
            )

        if "Memory" in agents:

            results["memory"] = (
                self.memory.get_customer_memory(
                    customer_id
                )
            )

        if "Order" in agents:

            results["orders"] = (
                self.order.monthly_orders(
                    customer_id
                )
            )

        return results