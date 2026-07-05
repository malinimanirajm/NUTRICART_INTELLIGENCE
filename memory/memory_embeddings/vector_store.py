#code
"""
memory/vector_store.py
"""

import numpy as np


class VectorStore:

    def __init__(self):

        self.store = {}

    def add(
        self,
        memory_id,
        embedding,
    ):

        self.store[memory_id] = embedding

    def get(
        self,
        memory_id,
    ):

        return self.store.get(memory_id)

    def all(self):

        return self.store.items()