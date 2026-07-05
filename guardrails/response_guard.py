"""
guardrails/response_guard.py
"""

from guardrails.models import GuardResult


class ResponseGuard:

    REQUIRED_KEYS = {

        "answer",

        "sources",

    }

    def validate(
        self,
        response: dict,
    ) -> GuardResult:

        missing = [

            key

            for key in self.REQUIRED_KEYS

            if key not in response

        ]

        if missing:

            return GuardResult(

                False,

                f"Missing keys: {missing}",

            )

        return GuardResult(True)