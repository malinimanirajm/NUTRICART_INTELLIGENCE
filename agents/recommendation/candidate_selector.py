"""
Candidate Selector

Retrieves candidate products from the Search Service.
"""

from __future__ import annotations

from agents.search.service import SearchService


class CandidateSelector:

    def __init__(self):

        self.search_service = SearchService()

    # ---------------------------------------------------------

    def get_candidates(
        self,
        customer_id: str,
        query: str,
        top_k: int = 100,
    ) -> list[dict]:

        """
        Returns candidate products for recommendation.
        """

        state = self.search_service.search(

            customer_id=customer_id,

            query=query,

            top_k=top_k,

        )

        #
        # Search Failed
        #

        if state.status != "success":

            return []

        #
        # No Products
        #

        if not state.products:

            return []

        return state.products

    # ---------------------------------------------------------

    def has_candidates(
        self,
        customer_id: str,
        query: str,
    ) -> bool:

        products = self.get_candidates(

            customer_id,

            query,

            top_k=1,

        )

        return len(products) > 0