from __future__ import annotations

from abc import ABC, abstractmethod


class MemoryRepository(ABC):
    """
    Base interface for memory repositories.
    """

    # ======================================================
    # Working Memory
    # ======================================================

    @abstractmethod
    def save_working(self, memory):
        ...

    @abstractmethod
    def get_working(self, customer_id):
        ...

    # ======================================================
    # Episodic Memory
    # ======================================================

    @abstractmethod
    def save_episode(self, episode):
        ...

    @abstractmethod
    def get_episodes(self, customer_id):
        ...

    # ======================================================
    # Semantic Memory
    # ======================================================

    @abstractmethod
    def save_semantic(self, memory):
        ...

    @abstractmethod
    def get_semantic(self, customer_id):
        ...

    # ======================================================
    # Preference Memory
    # ======================================================

    @abstractmethod
    def save_preference(self, preference):
        ...

    @abstractmethod
    def get_preference(self, customer_id):
        ...

    # ======================================================
    # Customer Profile
    # ======================================================

    @abstractmethod
    def save_profile(self, profile):
        ...

    @abstractmethod
    def get_profile(self, customer_id):
        ...

    # ======================================================
    # Health
    # ======================================================

    @abstractmethod
    def health(self) -> dict:
        ...