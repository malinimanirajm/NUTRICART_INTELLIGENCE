#code
"""
memory/semantic_search.py
"""

from memory.memory_embeddings.similarity import cosine_similarity


class SemanticSearch:

    def __init__(self, store):

        self.store = store

    def search(
        self,
        query_embedding,
        top_k=5,
    ):

        scores = []

        for memory_id, embedding in self.store.all():

            score = cosine_similarity(
                query_embedding,
                embedding,
            )

            scores.append((memory_id, score))

        scores.sort(
            key=lambda x: x[1],
            reverse=True,
        )

        return scores[:top_k]