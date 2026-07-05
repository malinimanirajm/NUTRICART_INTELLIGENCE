"""
memory/memory_reducer.py
"""

from collections import Counter

from memory.memory_types.semantic_memory import SemanticMemory


class MemoryReducer:
    """
    Converts episodic memories into semantic memories.
    """

    def __init__(
        self,
        min_occurrences: int = 3,
        keep_recent: int = 50,
    ):
        self.min_occurrences = min_occurrences
        self.keep_recent = keep_recent

    def reduce(
        self,
        customer_id: str,
        episodes: list,
    ):

        counter = Counter()

        for episode in episodes:

            category = episode.payload.get("category")

            if category:

                counter[category] += 1

        semantic = []

        total = max(len(episodes), 1)

        for category, count in counter.items():

            if count < self.min_occurrences:
                continue

            semantic.append(

                SemanticMemory(

                    customer_id=customer_id,

                    key="preferred_category",

                    value=category,

                    confidence=round(count / total, 2),

                )

            )

        remaining = sorted(

            episodes,

            key=lambda e: e.timestamp,

            reverse=True,

        )[: self.keep_recent]

        return semantic, remaining