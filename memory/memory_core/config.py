"""memory/config.py"""

"""
memory/config.py

Configuration for the Memory subsystem.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class MemoryConfig:

    database: str = "memory.db"

    embedding_model: str = "all-MiniLM-L6-v2"

    min_confidence: float = 0.6

    top_k: int = 10


config = MemoryConfig()