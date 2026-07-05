"""
Search Service

Responsibilities

1. Parse query
2. Validate filters
3. Build Weaviate filters
4. Execute Search
5. Save Search History
"""

import time

from agents.search.parser import SearchParser
from agents.search.validator import SearchValidator
from agents.search.filter_builder import FilterBuilder
from agents.search.repository import SearchRepository
from agents.search.search_state import SearchState

from memory.memory_service import MemoryService

from config.search_config import SEARCH_CONFIG
import traceback


class SearchService:

    def __init__(self):

        self.parser = SearchParser()

        self.validator = SearchValidator()

        self.builder = FilterBuilder()

        self.memory = MemoryService()

    # ---------------------------------------------------------

    def search(

        self,

        customer_id: str,

        query: str,

        top_k: int | None = None,

        alpha: float | None = None,

    ) -> SearchState:

        start = time.perf_counter()

        if top_k is None:
            top_k = SEARCH_CONFIG["default_top_k"]

        if alpha is None:
            alpha = SEARCH_CONFIG["default_alpha"]

        state = SearchState(

            customer_id=customer_id,

            query=query,

        )

        try:

            #
            # Empty query
            #

            query = query.strip()

            if not query:

                state.status = "failed"

                state.message = "Query cannot be empty."

                return state

            #
            # Parse
            #

            state.filters = self.parser.parse(query)


            print("=" * 60)
            print("PARSED FILTERS")
            print(state.filters)
            print("=" * 60)

            #
            # Validate
            #

            validation = self.validator.validate(

                state.filters

            )

            state.validation_errors = validation.errors

            if not validation.valid:

                state.status = "validation_failed"

                state.message = "Invalid filters."

                return state

            #
            # Build Weaviate Filter
            #

            state.weaviate_filter = self.builder.build(

                state.filters

            )

            #
            # Build Semantic Query
            #

            state.semantic_query = self._semantic_query(

                query,

                state.filters,

            )
            print("Semantic Query :", state.semantic_query)
            print("Weaviate Filter:", state.weaviate_filter)
            #
            # Save Search
            #
            print("Saving search to memory...")

            self.memory.search(

                customer_id=customer_id,

                query=query,

                filters={
                    "category": state.filters.category,
                    "brand": state.filters.brand,
                    "min_protein": state.filters.min_protein,
                    "max_protein": state.filters.max_protein,
                    "min_sugar": state.filters.min_sugar,
                    "max_sugar": state.filters.max_sugar,
                    "organic": state.filters.organic,
                    "vegan": state.filters.vegan,
                    "gluten_free": state.filters.gluten_free,
                    "diabetic": state.filters.diabetic,
                },

            )

            print("Search saved successfully.")
            #
            # Repository Search
            #
            print("=" * 60)
            print("Calling SearchRepository")
            print("=" * 60)

            with SearchRepository() as repository:

                state.products = repository.search(

                    query=state.semantic_query,

                    filters=state.weaviate_filter,

                    top_k=top_k,

                    alpha=alpha,

                    semantic=False

                )
            print("Products Returned:", len(state.products))
            print("Product Details:")   
            for p in state.products[:3]:
                print(getattr(p, "product_name", p))

            #
            # Success
            #

            state.status = "success"

            state.message = (

                f"Retrieved {len(state.products)} products."

            )

            return state

        except Exception as ex:

            print("=" * 60)
            print("SEARCH ERROR")
            traceback.print_exc()
            print("=" * 60)

            state.status = "failed"
            state.message = str(ex)

            return state

        finally:

            state.execution_time_ms = round(

                (

                    time.perf_counter()

                    - start

                ) * 1000,

                2,

            )

    # ---------------------------------------------------------

    def _semantic_query(

        self,

        query: str,

        filters,

    ) -> str:

        #
        # Category search
        #

        if filters.category:

            return filters.category

        #
        # Brand search
        #

        if filters.brand:

            return filters.brand

        #
        # Fallback
        #

        return query