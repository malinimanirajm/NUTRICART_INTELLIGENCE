"""
Recommendation Profile Builder
"""

from __future__ import annotations

from agents.recommendation.models import CustomerProfile
from memory.memory_service.memory_service import MemoryService


class ProfileBuilder:

    def __init__(self):

        self.memory = MemoryService()

    # ---------------------------------------------------------

    def build(
        self,
        customer_id: str,
    ) -> CustomerProfile:

        #
        # Recommendation profile
        #

        profile = CustomerProfile(
            customer_id=customer_id
        )

        #
        # Memory Service
        #

        memory = self.memory.get_customer_memory(
            customer_id
        )

        if memory is None:
            return profile

        stored_profile = memory.get("profile")

        if stored_profile is None:
            return profile

        #
        # Preference Memory
        #

        pref = stored_profile.preference_memory

        if pref:

            profile.preferred_protein = (
                pref.nutrition_preferences.get(
                    "protein"
                )
            )

            profile.preferred_calories = (
                pref.nutrition_preferences.get(
                    "calories"
                )
            )

            profile.preferred_sugar = (
                pref.nutrition_preferences.get(
                    "sugar"
                )
            )

            profile.diabetic = (
                "diabetic"
                in pref.dietary_preferences
            )

            profile.vegan = (
                "vegan"
                in pref.dietary_preferences
            )

            profile.gluten_free = (
                "gluten_free"
                in pref.dietary_preferences
            )

            profile.organic = (
                "organic"
                in pref.shopping_preferences
            )

        #
        # Semantic Memories
        #

        for semantic in stored_profile.semantic_memories:

            #
            # Categories
            #

            if semantic.key == "preferred_category":

                profile.favourite_categories.append(
                    semantic.value
                )

                profile.category_confidence[
                    semantic.value
                ] = semantic.confidence

            #
            # Brands
            #

            elif semantic.key == "preferred_brand":

                profile.favourite_brands.append(
                    semantic.value
                )

                profile.brand_confidence[
                    semantic.value
                ] = semantic.confidence

        return profile