from __future__ import annotations

from dataclasses import dataclass


# ==========================================================
# Result
# ==========================================================

@dataclass(slots=True)
class MemoryWorkflowResult:

    success: bool

    profile: object | None = None

    memories: object | None = None

    message: str = ""


# ==========================================================
# Orchestrator
# ==========================================================

class MemoryOrchestrator:

    def __init__(self, memory_service):

        self.memory = memory_service

    # =====================================================
    # Learn Workflow
    # =====================================================

    def learn(

        self,

        event_type,

        customer_id,

        **kwargs,

    ):

        self.memory.learn(

            event_type,

            customer_id,

            **kwargs,

        )

        self.memory.refresh(

            customer_id,

        )

        profile = self.memory.profile(

            customer_id,

        )

        return MemoryWorkflowResult(

            success=True,

            profile=profile,

            message="Learning completed.",

        )

    # =====================================================
    # Recommendation Workflow
    # =====================================================

    def recommendation(

        self,

        customer_id,

        query,

    ):

        context = self.memory.recommendation_context(

            customer_id,

            query,

        )

        return MemoryWorkflowResult(

            success=True,

            memories=context,

            message="Recommendation context ready.",

        )

    # =====================================================
    # Maintenance Workflow
    # =====================================================

    def maintenance(

        self,

        customer_id,

    ):

        self.memory.reduce(

            customer_id,

        )

        self.memory.refresh(

            customer_id,

        )

        profile = self.memory.profile(

            customer_id,

        )

        return MemoryWorkflowResult(

            success=True,

            profile=profile,

            message="Maintenance completed.",

        )

    # =====================================================
    # Customer Context
    # =====================================================

    def customer(

        self,

        customer_id,

    ):

        return self.memory.profile(

            customer_id,

        )

    # =====================================================
    # Health
    # =====================================================

    def health(self):

        return self.memory.health()

    # =====================================================
    # Python Helpers
    # =====================================================

    def __repr__(self):

        return (

            f"MemoryOrchestrator("

            f"service={type(self.memory).__name__})"

        )


__all__ = [

    "MemoryWorkflowResult",

    "MemoryOrchestrator",

]