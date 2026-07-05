"""
Recommendation Scoring Engine
"""

from __future__ import annotations

from agents.recommendation.models import (
    CustomerProfile,
    Recommendation,
)


class RecommendationScorer:

    def __init__(self):

        #
        # Score Weights
        #

        self.weights = {

            "category": 30,

            "brand": 20,

            "protein": 15,

            "calories": 10,

            "sugar": 10,

            "diet": 10,

            "organic": 5,

            "search": 5,

        }

    # ---------------------------------------------------------

    def score_products(

        self,

        profile: CustomerProfile,

        products: list[dict],

    ) -> list[Recommendation]:

        recommendations = []

        for product in products:

            recommendation = Recommendation(
                product=product
            )

            recommendation.score = self.score_product(
                profile,
                recommendation,
            )

            recommendations.append(
                recommendation
            )

        return recommendations

    # ---------------------------------------------------------

    def score_product(

        self,

        profile: CustomerProfile,

        recommendation: Recommendation,

    ) -> float:

        product = recommendation.product

        score = 0

        #
        # Category
        #

        score += self._category_score(

            profile,

            product,

            recommendation,

        )

        #
        # Brand
        #

        score += self._brand_score(

            profile,

            product,

            recommendation,

        )

        #
        # Nutrition
        #

        score += self._protein_score(

            profile,

            product,

            recommendation,

        )

        score += self._calorie_score(

            profile,

            product,

            recommendation,

        )

        score += self._sugar_score(

            profile,

            product,

            recommendation,

        )

        #
        # Dietary Preferences
        #

        score += self._diet_score(

            profile,

            product,

            recommendation,

        )

        score += self._organic_score(

            profile,

            product,

            recommendation,

        )

        #
        # Existing Search Score
        #

        score += self._search_score(
            product,
        )

        return round(score, 2)

    # =========================================================
    # Category
    # =========================================================

        # =========================================================
    # Category
    # =========================================================

    def _category_score(
        self,
        profile,
        product,
        recommendation,
    ) -> float:

        category = product.get("category_name")

        confidence = profile.category_confidence.get(
            category,
            0.0,
        )

        if confidence <= 0:
            return 0

        recommendation.reasons.append(
            f"Preferred category ({confidence:.2f})"
        )

        return round(
            self.weights["category"] * confidence,
            2,
        )

    # =========================================================
    # Brand
    # =========================================================

    def _brand_score(
        self,
        profile,
        product,
        recommendation,
    ) -> float:

        brand = product.get("brand_name")

        confidence = profile.brand_confidence.get(
            brand,
            0.0,
        )

        if confidence <= 0:
            return 0

        recommendation.reasons.append(
            f"Preferred brand ({confidence:.2f})"
        )

        return round(
            self.weights["brand"] * confidence,
            2,
        )

    # =========================================================
    # Protein
    # =========================================================

    def _protein_score(
        self,
        profile,
        product,
        recommendation,
    ) -> float:

        target = profile.preferred_protein

        value = product.get("protein_g")

        if target is None or value is None:
            return 0

        if value >= target:

            recommendation.reasons.append(
                "High protein"
            )

            return self.weights["protein"]

        return 0

    # =========================================================
    # Calories
    # =========================================================

    def _calorie_score(
        self,
        profile,
        product,
        recommendation,
    ) -> float:

        target = profile.preferred_calories

        value = product.get("calories_100g")

        if target is None or value is None:
            return 0

        if value <= target:

            recommendation.reasons.append(
                "Low calorie"
            )

            return self.weights["calories"]

        return 0

    # =========================================================
    # Sugar
    # =========================================================

    def _sugar_score(
        self,
        profile,
        product,
        recommendation,
    ) -> float:

        target = profile.preferred_sugar

        value = product.get("added_sugar_g")

        if target is None or value is None:
            return 0

        if value <= target:

            recommendation.reasons.append(
                "Low sugar"
            )

            return self.weights["sugar"]

        return 0

    # =========================================================
    # Diet
    # =========================================================
    def _diet_score(
        self,
        profile,
        product,
        recommendation,
    ) -> float:

        score = 0

        if profile.diabetic and product.get(
            "diabetic_friendly"
        ):

            score += 5

            recommendation.reasons.append(
                "Diabetic friendly"
            )

        if profile.vegan and product.get(
            "is_vegan"
        ):

            score += 5

            recommendation.reasons.append(
                "Vegan"
            )

        if profile.gluten_free and product.get(
            "is_gluten_free"
        ):

            score += 5

            recommendation.reasons.append(
                "Gluten free"
            )

        return score

    # =========================================================
    # Organic
    # =========================================================

    def _organic_score(
        self,
        profile,
        product,
        recommendation,
    ) -> float:

        if (
            profile.organic
            and
            product.get("is_organic_available")
        ):

            recommendation.reasons.append(
                "Organic"
            )

            return self.weights["organic"]

        return 0

    # =========================================================
    # Search Score
    # =========================================================

    def _search_score(
        self,
        product,
    ) -> float:

        score = product.get(
            "score",
            0,
        )

        if score is None:
            return 0

        #
        # Hybrid search score from Weaviate.
        # Used only as a tie-breaker.
        #

        return round(
            score * self.weights["search"],
            2,
        )