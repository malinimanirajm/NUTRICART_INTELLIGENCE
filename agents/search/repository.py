"""
Search Repository

Supports
--------
1. Structured Filter Search
2. BM25 Keyword Search
3. Hybrid Search
4. Get Product By ID

Compatible with Weaviate Client 4.20.4
"""

from typing import List, Optional

import weaviate
from weaviate.classes.query import MetadataQuery, Filter
from weaviate.collections.classes.filters import _Filters


class SearchRepository:

    def __init__(self):

        self.client = weaviate.connect_to_local()

        self.collection = self.client.collections.get(
            "NutricartUnified"
        )

    # ------------------------------------------------------------------

    def _objects_to_products(
        self,
        response,
    ) -> List[dict]:

        products = []

        seen = set()

        for obj in response.objects:

            product = dict(obj.properties)

            metadata = getattr(
                obj,
                "metadata",
                None,
            )

            score = 0.0

            if metadata is not None:

                metadata_score = getattr(
                    metadata,
                    "score",
                    None,
                )

                if metadata_score is not None:

                    score = float(metadata_score)

            product["score"] = score

            product_id = product.get(
                "product_id"
            )

            if product_id in seen:
                continue

            seen.add(product_id)

            products.append(product)

        return products

    # ------------------------------------------------------------------

    def get_product(
        self,
        product_id: str,
    ) -> Optional[dict]:

        response = self.collection.query.fetch_objects(

            filters=Filter.by_property(
                "product_id"
            ).equal(product_id),

            limit=1,

        )

        products = self._objects_to_products(
            response
        )

        if not products:
            return None

        return products[0]

    # ------------------------------------------------------------------

    def filter_search(
        self,
        filters: _Filters,
        top_k: int = 10,
    ) -> List[dict]:

        response = self.collection.query.fetch_objects(

            filters=filters,

            limit=top_k,

        )

        return self._objects_to_products(
            response
        )

    # ------------------------------------------------------------------

    def keyword_search(
        self,
        query: str,
        filters: Optional[_Filters] = None,
        top_k: int = 10,
    ) -> List[dict]:

        response = self.collection.query.bm25(

            query=query,

            filters=filters,

            limit=top_k,

            return_metadata=MetadataQuery(
                score=True
            ),

        )

        return self._objects_to_products(
            response
        )

    # ------------------------------------------------------------------

    def hybrid_search(
        self,
        query: str,
        filters: Optional[_Filters] = None,
        top_k: int = 10,
        alpha: float = 0.5,
    ) -> List[dict]:

        response = self.collection.query.hybrid(

            query=query,

            filters=filters,

            alpha=alpha,

            limit=top_k,

            return_metadata=MetadataQuery(
                score=True
            ),

        )

        return self._objects_to_products(
            response
        )

    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        filters: Optional[_Filters] = None,
        top_k: int = 10,
        alpha: float = 0.5,
        semantic: bool = False,
    ) -> List[dict]:

        if filters is not None:

            print(
                "Repository -> FILTER SEARCH"
            )

            return self.filter_search(

                filters=filters,

                top_k=top_k,

            )

        if semantic:

            print(
                "Repository -> HYBRID SEARCH"
            )

            return self.hybrid_search(

                query=query,

                top_k=top_k,

                alpha=alpha,

            )

        print(
            "Repository -> BM25 SEARCH"
        )

        return self.keyword_search(

            query=query,

            top_k=top_k,

        )

    # ------------------------------------------------------------------

    def close(self):

        self.client.close()

    # ------------------------------------------------------------------

    def __enter__(self):

        return self

    # ------------------------------------------------------------------

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ):

        self.close()