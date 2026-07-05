"""
guardrails/input_guard.py
"""

import re

from guardrails.models import GuardResult


class InputGuard:

    MAX_QUERY_LENGTH = 500

    BLOCKED_PATTERNS = [

        r"ignore previous instructions",

        r"system prompt",

        r"delete database",

        r"drop table",

        r"<script",

    ]

    def validate(
        self,
        query: str,
    ) -> GuardResult:

        if not query:

            return GuardResult(

                False,

                "Query is empty.",

            )

        query = query.strip()

        if len(query) > self.MAX_QUERY_LENGTH:

            return GuardResult(

                False,

                "Query too long.",

            )

        lower = query.lower()

        for pattern in self.BLOCKED_PATTERNS:

            if re.search(pattern, lower):

                return GuardResult(

                    False,

                    f"Blocked pattern: {pattern}",

                )

        return GuardResult(True)