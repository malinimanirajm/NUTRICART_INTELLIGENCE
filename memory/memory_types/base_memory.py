from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime


@dataclass(slots=True)
class BaseMemory:
    """
    Base class for all memory types.
    """

    customer_id: str

    created_at: datetime = field(default_factory=datetime.utcnow)

    updated_at: datetime = field(default_factory=datetime.utcnow)

    def touch(self) -> None:
        """
        Update the modification timestamp.
        """
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        Convert the object to a dictionary.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create an object from a dictionary.
        """
        return cls(**data)