"""
memory/memory_retriever.py
"""

from memory.memory_intelligence.memory_ranker import MemoryRanker


class MemoryRetriever:
    """
    Retrieves relevant memories.
    """

    def __init__(
        self,
        repository,
        ranker: MemoryRanker | None = None,
    ):
        self.repository = repository
        self.ranker = ranker or MemoryRanker()

    def retrieve(
        self,
        customer_id: str,
        top_k: int = 10,
    ):

        memories = []

        memories.extend(
            self.repository.get_semantic(customer_id) or []
        )

        memories.extend(
            self.repository.get_episodes(customer_id) or []
        )

        ranked = self.ranker.rank(memories)

        return ranked[:top_k]