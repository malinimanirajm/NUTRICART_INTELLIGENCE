"""
Recommendation Service

Pipeline

Query
    ↓
Candidate Selection
    ↓
Customer Profile
    ↓
Scoring
    ↓
Ranking
    ↓
Explanation
    ↓
Recommendation Result
"""

from __future__ import annotations

from agents.recommendation.candidate_selector import CandidateSelector
from agents.recommendation.explanation import ExplanationGenerator
from agents.recommendation.models import RecommendationResult
from agents.recommendation.profile_builder import ProfileBuilder
from agents.recommendation.ranker import RecommendationRanker
from agents.recommendation.scoring import RecommendationScorer


class RecommendationService:

    def __init__(self):

        self.selector = CandidateSelector()

        self.profile_builder = ProfileBuilder()

        self.scorer = RecommendationScorer()

        self.ranker = RecommendationRanker()

        self.explainer = ExplanationGenerator()

    # ---------------------------------------------------------

    def recommend(
        self,
        customer_id: str,
        query: str,
        top_k: int = 10,
    ) -> RecommendationResult:

        result = RecommendationResult(
            customer_id=customer_id,
            query=query,
        )

        # =====================================================
        # Build Customer Profile
        # =====================================================

        profile = self.profile_builder.build(customer_id)

        print("=" * 80)
        print("PROFILE TYPE:", type(profile))

        if hasattr(profile, "preference_memory"):
            print("PREFERENCE TYPE:", type(profile.preference_memory))
            print("PREFERENCE:", profile.preference_memory)

        print("=" * 80)

        # =====================================================
        # Candidate Selection
        # =====================================================

        candidates = self.selector.get_candidates(
            customer_id=customer_id,
            query=query,
            top_k=100,
        )

        if not candidates:

            result.status = "success"
            result.message = "No recommendations found."

            return result

        # =====================================================
        # Score Candidates
        # =====================================================

        recommendations = self.scorer.score_products(
            profile,
            candidates,
        )

        # =====================================================
        # Rank
        # =====================================================

        recommendations = self.ranker.rank(
            recommendations,
            top_k=top_k,
        )

        # =====================================================
        # Explain
        # =====================================================

        recommendations = self.explainer.generate(
            recommendations,
        )

        result.recommendations = recommendations

        result.message = (
            f"Generated {len(recommendations)} recommendations."
        )

        return result

    # ---------------------------------------------------------

    def recommend_products(
        self,
        customer_id: str,
        query: str,
        top_k: int = 10,
    ):

        """
        Convenience API.

        Returns only product dictionaries.
        """

        result = self.recommend(

            customer_id,

            query,

            top_k,

        )

        return [

            recommendation.product

            for recommendation in result.recommendations

        ]

    # ---------------------------------------------------------

    def explain(
        self,
        customer_id: str,
        query: str,
        top_k: int = 5,
    ):

        result = self.recommend(

            customer_id,

            query,

            top_k,

        )

        explanations = []

        for recommendation in result.recommendations:

            explanations.append(

                self.explainer.detailed_explanation(

                    recommendation

                )

            )

        return explanations