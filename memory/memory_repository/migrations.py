"""memory/migrations.py"""

# Placeholder implementation.
"""
memory/migrations.py

Simple database migrations.
"""

from __future__ import annotations

from memory.memory_repository.schema import create_schema


class MigrationManager:
    """
    Executes database migrations.
    """

    VERSION = 1

    def __init__(self, connection):

        self.connection = connection

    # =====================================================
    # Public
    # =====================================================

    def migrate(self):

        self._create_version_table()

        version = self.current_version()

        if version < self.VERSION:

            create_schema(self.connection)

            self._set_version(self.VERSION)

    # =====================================================
    # Version
    # =====================================================

    def current_version(self) -> int:

        cursor = self.connection.execute(

            "SELECT version FROM schema_version LIMIT 1"

        )

        row = cursor.fetchone()

        return row[0] if row else 0

    # =====================================================
    # Helpers
    # =====================================================

    def _create_version_table(self):

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version(
                version INTEGER NOT NULL
            )
            """
        )

        self.connection.commit()

    def _set_version(self, version: int):

        self.connection.execute(
            "DELETE FROM schema_version"
        )

        self.connection.execute(
            "INSERT INTO schema_version(version) VALUES(?)",
            (version,),
        )

        self.connection.commit()