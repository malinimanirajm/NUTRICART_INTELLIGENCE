from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Any

logger = logging.getLogger(__name__)


# ==========================================================
# Job Result
# ==========================================================

@dataclass(slots=True)
class JobResult:
    job_name: str
    success: bool
    started_at: datetime
    completed_at: datetime
    processed: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)


# ==========================================================
# Scheduler
# ==========================================================

class MemoryScheduler:
    """
    Executes background maintenance jobs.

    This class does NOT store memory.
    It simply invokes MemoryService methods
    on a schedule (cron/APScheduler/Celery/etc.).
    """

    def __init__(
        self,
        memory_service,
        customer_repository,
    ):

        self.memory_service = memory_service
        self.customer_repository = customer_repository

    # =====================================================
    # Public Jobs
    # =====================================================

    def refresh_memories(self) -> JobResult:

        return self._run_for_all_customers(

            "refresh_memories",

            self.memory_service.refresh,

        )

    # -----------------------------------------------------

    def reduce_memories(self) -> JobResult:

        return self._run_for_all_customers(

            "reduce_memories",

            self.memory_service.reduce,

        )

    # -----------------------------------------------------

    def rebuild_preferences(self) -> JobResult:

        return self._run_for_all_customers(

            "rebuild_preferences",

            self.memory_service.update_preferences,

        )

    # -----------------------------------------------------

    def archive_old_memories(self) -> JobResult:

        return self._run_for_all_customers(

            "archive_old_memories",

            self.memory_service.archive_old_memories,

        )

    # -----------------------------------------------------

    def maintenance(self) -> dict:

        return {

            "refresh": self.refresh_memories(),

            "reduce": self.reduce_memories(),

            "preferences": self.rebuild_preferences(),

            "archive": self.archive_old_memories(),

        }

    # =====================================================
    # Runner
    # =====================================================

    def _run_for_all_customers(

        self,

        job_name: str,

        operation: Callable[[str], Any],

    ) -> JobResult:

        started = datetime.utcnow()

        processed = 0

        failed = 0

        errors = []

        customers = self.customer_repository.list()

        for customer in customers:

            try:

                operation(customer.customer_id)

                processed += 1

            except Exception as exc:

                failed += 1

                errors.append(

                    f"{customer.customer_id}: {exc}"

                )

                logger.exception(exc)

        return JobResult(

            job_name=job_name,

            success=failed == 0,

            started_at=started,

            completed_at=datetime.utcnow(),

            processed=processed,

            failed=failed,

            errors=errors,

        )

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict:

        return {

            "status": "healthy",

            "service": type(self.memory_service).__name__,

            "repository": type(self.customer_repository).__name__,

        }

    # =====================================================
    # Python Helpers
    # =====================================================

    def __repr__(self):

        return (

            f"MemoryScheduler("

            f"service={type(self.memory_service).__name__})"

        )


__all__ = [

    "JobResult",

    "MemoryScheduler",

]