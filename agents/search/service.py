"""
Search Service

Responsibilities
----------------
1. Orchestrate search workflow
2. Parse query
3. Validate filters
4. Build Weaviate filters
5. Execute Hybrid Search
6. Save Search History
7. Update Search State
8. Return SearchState

No Weaviate logic
No parsing logic
No validation logic
"""

import time

from graph.states.search_state import SearchState
from agents.search.parser import SearchParser
from agents.search.validator import SearchValidator
from agents.search.filter_builder import FilterBuilder
from agents.search.repository import SearchRepository

from agents.memory_agent import MemoryAgent


class SearchService:

    def __init__(self):

        self.parser = SearchParser()

        self.validator = SearchValidator()

        self.builder = FilterBuilder()

        self.memory = MemoryAgent()

    # ---------------------------------------------------------

    def search(

        self,

        customer_id: str,

        query: str,

        top_k: int = 10,

        alpha: float = 0.5

    ) -> SearchState:

        start = time.perf_counter()

        # -----------------------------------------------------
        # Initialize State
        # -----------------------------------------------------

        state = SearchState(

            customer_id=customer_id,

            query=query

        )

        try:

            # -------------------------------------------------
            # Step 1 Parse
            # -------------------------------------------------

            state.filters = self.parser.parse(

                state.query

            )

            # -------------------------------------------------
            # Step 2 Validate
            # -------------------------------------------------

            validation = self.validator.validate(

                state.filters

            )

            state.validation_errors = validation.errors

            if not validation.valid:

                state.status = "validation_failed"

                state.message = "Search filters are invalid."

                return state

            # -------------------------------------------------
            # Step 3 Save Search
            # -------------------------------------------------

            self.memory.save_search(

                customer_id=state.customer_id,

                query=state.query,

                category=state.filters.category or "Unknown"

            )

            # -------------------------------------------------
            # Step 4 Build Weaviate Filter
            # -------------------------------------------------

            state.weaviate_filter = self.builder.build(

                state.filters

            )

            # -------------------------------------------------
            # Step 5 Build Semantic Query
            # -------------------------------------------------

            state.semantic_query = self._semantic_query(

                state.query,

                state.filters

            )

            # -------------------------------------------------
            # Step 6 Repository Search
            # -------------------------------------------------

            with SearchRepository() as repository:

                state.products = repository.hybrid_search(

                    query=state.semantic_query,

                    filters=state.weaviate_filter,

                    top_k=top_k,

                    alpha=alpha

                )

            # -------------------------------------------------
            # Step 7 Complete
            # -------------------------------------------------

            state.status = "success"

            state.message = (

                f"Retrieved {len(state.products)} products."

            )

            return state

        except Exception as ex:

            state.status = "failed"

            state.message = str(ex)

            return state

        finally:

            state.execution_time_ms = round(

                (time.perf_counter() - start) * 1000,

                2

            )

    # ---------------------------------------------------------

    def _semantic_query(

        self,

        query: str,

        filters

    ) -> str:

        """
        Convert user query into a cleaner semantic query.

        Examples
        --------

        Show beverages with >20g protein

        →

        Beverages

        Quest protein bars

        →

        Quest

        """

        if filters.brand:

            return filters.brand

        if filters.category:

            return filters.category

        return query