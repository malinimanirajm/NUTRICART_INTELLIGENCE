"""
Search Repository

Responsibilities
----------------
1. Connect to Weaviate
2. Execute Hybrid / Vector / BM25 Search
3. Apply Filters
4. Return Products

No Parser
No Validator
No Memory
No LangGraph
"""

from typing import List, Optional

import weaviate

from weaviate.classes.query import MetadataQuery
from weaviate.collections.classes.filters import _Filters


class SearchRepository:

    def __init__(self):

        self.client = weaviate.connect_to_local()

        # Change this later to NutricartCatalog
        self.collection = self.client.collections.get(
            "NutricartUnified"
        )

    # --------------------------------------------------

    def hybrid_search(
        self,
        query: str,
        filters: Optional[_Filters] = None,
        top_k: int = 10,
        alpha: float = 0.5
    ) -> List[dict]:

        response = self.collection.query.hybrid(

            query=query,

            filters=filters,

            alpha=alpha,

            limit=top_k,

            return_metadata=MetadataQuery(score=True)

        )

        return self._parse_response(response)

    # --------------------------------------------------

    def vector_search(
        self,
        query: str,
        filters: Optional[_Filters] = None,
        top_k: int = 10
    ):

        response = self.collection.query.near_text(

            query=query,

            filters=filters,

            limit=top_k,

            return_metadata=MetadataQuery(score=True)

        )

        return self._parse_response(response)

    # --------------------------------------------------

    def keyword_search(
        self,
        query: str,
        filters: Optional[_Filters] = None,
        top_k: int = 10
    ):

        response = self.collection.query.bm25(

            query=query,

            filters=filters,

            limit=top_k,

            return_metadata=MetadataQuery(score=True)

        )

        return self._parse_response(response)

    # --------------------------------------------------

    def _parse_response(self, response):

        products = []

        for obj in response.objects:

            data = obj.properties.copy()

            if obj.metadata:

                data["score"] = obj.metadata.score

            products.append(data)

        return products

    # --------------------------------------------------

    def close(self):

        self.client.close()

    # --------------------------------------------------

    def __enter__(self):

        return self

    # --------------------------------------------------

    def __exit__(

        self,

        exc_type,

        exc_val,

        exc_tb

    ):

        self.close()