#code
"""
memory/embedding_cache.py
"""

class EmbeddingCache:

    def __init__(self):

        self.cache = {}

    def get(self, key):

        return self.cache.get(key)

    def put(
        self,
        key,
        embedding,
    ):

        self.cache[key] = embedding