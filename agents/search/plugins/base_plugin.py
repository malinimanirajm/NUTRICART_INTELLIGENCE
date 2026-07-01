from abc import ABC, abstractmethod


class SearchPlugin(ABC):

    @abstractmethod
    def apply(
        self,
        query: str,
        filters
    ):
        pass