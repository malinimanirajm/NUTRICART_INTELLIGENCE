"""
memory/memory_ranker.py
"""

from datetime import datetime


class MemoryRanker:
    """
    Ranks memories by confidence and recency.
    """

    def score(self, memory) -> float:

        confidence = getattr(
            memory,
            "confidence",
            0.5,
        )

        age = (
            datetime.utcnow() -
            memory.updated_at
        ).days

        recency = max(
            0,
            30 - age,
        ) / 30

        return round(

            0.7 * confidence +

            0.3 * recency,

            2,

        )

    def rank(self, memories: list):

        return sorted(

            memories,

            key=self.score,

            reverse=True,

        )