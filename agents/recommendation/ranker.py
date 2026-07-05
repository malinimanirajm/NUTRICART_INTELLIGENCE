"""
Recommendation Ranker
"""

from __future__ import annotations

from agents.recommendation.models import Recommendation


class RecommendationRanker:

    # ---------------------------------------------------------

    def rank(
        self,
        recommendations: list[Recommendation],
        top_k: int = 10,
    ) -> list[Recommendation]:
        """
        Sort recommendations by score.
        """

        recommendations = sorted(
            recommendations,
            key=lambda recommendation: recommendation.score,
            reverse=True,
        )

        recommendations = self._remove_duplicates(
            recommendations
        )

        return recommendations[:top_k]

    # ---------------------------------------------------------

    def _remove_duplicates(
        self,
        recommendations: list[Recommendation],
    ) -> list[Recommendation]:

        seen = set()

        ranked = []

        for recommendation in recommendations:

            product = recommendation.product

            product_id = product.get(
                "product_id"
            )

            if product_id in seen:
                continue

            seen.add(product_id)

            ranked.append(
                recommendation
            )

        return ranked

    # ---------------------------------------------------------

    def top_score(
        self,
        recommendations: list[Recommendation],
    ) -> float:

        if not recommendations:
            return 0.0

        return max(
            recommendation.score
            for recommendation in recommendations
        )

    # ---------------------------------------------------------

    def average_score(
        self,
        recommendations: list[Recommendation],
    ) -> float:

        if not recommendations:
            return 0.0

        total = sum(
            recommendation.score
            for recommendation in recommendations
        )

        return round(
            total / len(recommendations),
            2,
        )

    # ---------------------------------------------------------

    def filter_by_score(
        self,
        recommendations: list[Recommendation],
        minimum_score: float,
    ) -> list[Recommendation]:

        return [

            recommendation

            for recommendation in recommendations

            if recommendation.score >= minimum_score

        ]