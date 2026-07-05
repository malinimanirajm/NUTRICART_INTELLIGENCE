from __future__ import annotations

from memory.memory_repository.sqlite_repository import SQLiteMemoryRepository
from memory.memory_intelligence.semantic_builder import SemanticBuilder
from memory.memory_intelligence.memory_validator import MemoryValidator
from memory.memory_intelligence.memory_reducer import MemoryReducer
from memory.memory_intelligence.memory_retriever import MemoryRetriever
from memory.memory_types.preference_memory import PreferenceMemory
from memory.memory_types.customer_profile import CustomerProfile


class MemoryPipeline:

    def __init__(self):

        self.repo = SQLiteMemoryRepository()

        self.semantic_builder = SemanticBuilder()

        self.validator = MemoryValidator()

        self.reducer = MemoryReducer()

        self.retriever = MemoryRetriever(
            repository=self.repo
        )

    # =====================================================

    def learn(self, episode):

        customer_id = episode.customer_id

        print("=" * 80)
        print("MEMORY PIPELINE")
        print("Customer :", customer_id)
        print("=" * 80)

        #
        # Save Episode
        #

        self.repo.save_episode(episode)

        episodes = self.repo.get_episodes(customer_id)

        print("Episodes :", len(episodes))

        #
        # Build Semantic Memory
        #

        semantic = self.semantic_builder.build(
            customer_id,
            episodes,
        )

        print("=" * 80)
        print("AFTER BUILD")
        print(semantic)

        #
        # Validate
        #

        semantic = self.validator.validate(
            semantic
        )

        print("=" * 80)
        print("AFTER VALIDATOR")
        print(semantic)

        #
        # Replace semantic memories
        #

        print("Replacing semantic memories...")

        self.repo.replace_semantic(
            customer_id,
            semantic,
        )

        saved_semantic = self.repo.get_semantic(
            customer_id
        )

        print("=" * 80)
        print("AFTER SAVE")
        print(saved_semantic)
        print("=" * 80)

        #
        # Preference Memory
        #

        preference = PreferenceMemory.from_semantic(
            customer_id,
            saved_semantic,
        )

        print("=" * 80)
        print("PREFERENCE")
        print(preference)
        print("=" * 80)

        self.repo.save_preference(
            preference
        )

        #
        # Customer Profile
        #

        profile = self.repo.get_profile(
            customer_id
        )

        if profile is None:

            profile = CustomerProfile(
                customer_id=customer_id
            )

        profile.preference_memory = preference
        profile.semantic_memories = saved_semantic
        profile.episodic_memories = episodes

        self.repo.save_profile(
            profile
        )

        return preference

    # =====================================================

    def retrieve(
        self,
        customer_id,
        query,
        top_k=10,
    ):

        return self.retriever.retrieve(
            customer_id,
            query,
            top_k,
        )

    # =====================================================

    def reduce(
        self,
        customer_id,
    ):

        episodes = self.repo.get_episodes(
            customer_id
        )

        semantic, _ = self.reducer.reduce(
            customer_id,
            episodes,
        )

        semantic = self.validator.validate(
            semantic
        )

        self.repo.replace_semantic(
            customer_id,
            semantic,
        )

        return semantic

    # =====================================================

    def refresh(
        self,
        customer_id,
    ):

        episodes = self.repo.get_episodes(
            customer_id
        )

        semantic = self.semantic_builder.build(
            customer_id,
            episodes,
        )

        semantic = self.validator.validate(
            semantic
        )

        self.repo.replace_semantic(
            customer_id,
            semantic,
        )

        return semantic

    # =====================================================

    def profile(
        self,
        customer_id,
    ):

        return self.repo.get_profile(
            customer_id
        )

    # =====================================================

    def recommendation_context(
        self,
        customer_id,
        query,
    ):

        return {
            "profile": self.profile(customer_id),
            "memories": self.retrieve(
                customer_id,
                query,
            ),
        }

    # =====================================================

    def health(self):

        return self.repo.health()