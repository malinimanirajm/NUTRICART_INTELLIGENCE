"""memory/transaction.py"""

# Placeholder implementation.
"""
memory/transaction.py

SQLite transaction manager.
"""

from __future__ import annotations


class Transaction:
    """
    Context manager for SQLite transactions.

    Example:
        with Transaction(connection):
            ...
    """

    def __init__(self, connection):

        self.connection = connection

    def __enter__(self):

        self.connection.execute("BEGIN")

        return self.connection

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        if exc_type is None:

            self.connection.commit()

        else:

            self.connection.rollback()

        return False