from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ==========================================================
# Agent State
# ==========================================================

class AgentState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


# ==========================================================
# Conversation Message
# ==========================================================

@dataclass(slots=True)
class ConversationMessage:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ==========================================================
# Working Memory
# ==========================================================

@dataclass(slots=True)
class WorkingMemory:
    """
    Temporary memory for a single user session.
    """

    customer_id: str

    session_id: str = ""

    query: str = ""

    state: AgentState = AgentState.CREATED

    created_at: datetime = field(default_factory=datetime.utcnow)

    updated_at: datetime = field(default_factory=datetime.utcnow)

    conversation: list[ConversationMessage] = field(default_factory=list)

    context: dict[str, Any] = field(default_factory=dict)

    retrieved_memories: list[Any] = field(default_factory=list)

    retrieved_products: list[Any] = field(default_factory=list)

    reasoning_steps: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    # =====================================================
    # Conversation
    # =====================================================

    def add_message(
        self,
        role: str,
        content: str,
    ):

        self.conversation.append(

            ConversationMessage(

                role=role,

                content=content,

            )

        )

        self.updated_at = datetime.utcnow()

    # =====================================================
    # Memories
    # =====================================================

    def add_memory(self, memory):

        self.retrieved_memories.append(memory)

        self.updated_at = datetime.utcnow()

    # =====================================================
    # Products
    # =====================================================

    def add_product(self, product):

        self.retrieved_products.append(product)

        self.updated_at = datetime.utcnow()

    # =====================================================
    # Reasoning
    # =====================================================

    def add_reasoning(self, step: str):

        self.reasoning_steps.append(step)

        self.updated_at = datetime.utcnow()

    # =====================================================
    # Metadata
    # =====================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ):

        self.metadata[key] = value

        self.updated_at = datetime.utcnow()

    # =====================================================
    # State
    # =====================================================

    def set_state(
        self,
        state: AgentState,
    ):

        self.state = state

        self.updated_at = datetime.utcnow()

    # =====================================================
    # Reset
    # =====================================================

    def reset(self):

        self.state = AgentState.CREATED

        self.conversation.clear()

        self.context.clear()

        self.retrieved_memories.clear()

        self.retrieved_products.clear()

        self.reasoning_steps.clear()

        self.metadata.clear()

        self.updated_at = datetime.utcnow()

    # =====================================================
    # Serialization
    # =====================================================

    def to_dict(self):

        return {

            "customer_id": self.customer_id,

            "session_id": self.session_id,

            "query": self.query,

            "state": self.state.value,

            "conversation": [

                {

                    "role": m.role,

                    "content": m.content,

                    "timestamp": m.timestamp.isoformat(),

                }

                for m in self.conversation

            ],

            "context": self.context,

            "metadata": self.metadata,

        }


__all__ = [
    "AgentState",
    "ConversationMessage",
    "WorkingMemory",
]