"""
Recommendation Explanation Generator
"""

from __future__ import annotations

from agents.recommendation.models import Recommendation


class ExplanationGenerator:

    def generate(
        self,
        recommendations: list[Recommendation],
    ) -> list[Recommendation]:
        """
        Generate explanations for every recommendation.
        """

        for recommendation in recommendations:

            recommendation.reasons = self._clean_reasons(
                recommendation.reasons
            )

        return recommendations

    # ---------------------------------------------------------

    def explanation(
        self,
        recommendation: Recommendation,
    ) -> str:
        """
        Returns a readable explanation.
        """

        if not recommendation.reasons:

            return "Recommended based on your search."

        return "Recommended because: " + ", ".join(
            recommendation.reasons
        )

    # ---------------------------------------------------------

    def detailed_explanation(
        self,
        recommendation: Recommendation,
    ) -> str:

        product = recommendation.product

        lines = []

        lines.append(
            f"Product : {product.get('product_name')}"
        )

        lines.append(
            f"Score   : {recommendation.score}"
        )

        lines.append("")

        lines.append("Why this product?")

        for reason in recommendation.reasons:

            lines.append(f"✓ {reason}")

        return "\n".join(lines)

    # ---------------------------------------------------------

    def _clean_reasons(
        self,
        reasons: list[str],
    ) -> list[str]:

        unique = []

        seen = set()

        for reason in reasons:

            if reason in seen:
                continue

            seen.add(reason)

            unique.append(reason)

        return unique

    # ---------------------------------------------------------

    def add_reason(
        self,
        recommendation: Recommendation,
        reason: str,
    ):

        recommendation.reasons.append(reason)

    # ---------------------------------------------------------

    def clear(
        self,
        recommendation: Recommendation,
    ):

        recommendation.reasons.clear()