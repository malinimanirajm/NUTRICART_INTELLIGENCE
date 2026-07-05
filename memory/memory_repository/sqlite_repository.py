from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Optional

from memory.memory_repository.memory_repository import MemoryRepository

from memory.memory_types.working_memory import WorkingMemory
from memory.memory_types.episodic_memory import (
    EpisodicMemory,
    Episode,
    EpisodeType,
)
from memory.memory_types.semantic_memory import SemanticMemory
from memory.memory_types.preference_memory import PreferenceMemory
from memory.memory_types.customer_profile import CustomerProfile


class SQLiteMemoryRepository(MemoryRepository):

    # =====================================================
    # Constructor
    # =====================================================

    def __init__(
        self,
        db_path: str = "memory.db",
    ):

        self.connection = sqlite3.connect(db_path)

        self.connection.row_factory = sqlite3.Row

        self._create_tables()

    # =====================================================
    # Schema
    # =====================================================

    def _create_tables(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS working_memory(

                customer_id TEXT PRIMARY KEY,

                data TEXT NOT NULL

            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS episodic_memory(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                customer_id TEXT NOT NULL,

                timestamp TEXT NOT NULL,

                data TEXT NOT NULL

            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS semantic_memory (

            memory_id TEXT PRIMARY KEY,

            customer_id TEXT NOT NULL,

            memory_key TEXT NOT NULL,

            memory_value TEXT NOT NULL,

            data TEXT NOT NULL

        );
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS preference_memory(

                customer_id TEXT PRIMARY KEY,

                data TEXT NOT NULL

            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customer_profile(

                customer_id TEXT PRIMARY KEY,

                data TEXT NOT NULL

            )
            """
        )

        self.connection.commit()

    # =====================================================
    # Serializer
    # =====================================================

    def _serialize(
        self,
        obj,
    ) -> str:

        if hasattr(obj, "to_dict"):

            return json.dumps(obj.to_dict())

        if hasattr(obj, "__dict__"):

            return json.dumps(obj.__dict__)

        return json.dumps(obj)

    # =====================================================

    def _deserialize(
        self,
        value: str,
    ):

        if value is None:

            return None

        return json.loads(value)

    # =====================================================
    # Working Memory
    # =====================================================

    def save_working(
        self,
        memory: WorkingMemory,
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO working_memory
            VALUES (?,?)
            """,
            (
                memory.customer_id,
                self._serialize(memory),
            ),
        )

        self.connection.commit()

    # -----------------------------------------------------

    def get_working(
        self,
        customer_id: str,
    ) -> Optional[WorkingMemory]:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT data
            FROM working_memory
            WHERE customer_id=?
            """,
            (customer_id,),
        )

        row = cursor.fetchone()

        if row is None:

            return None

        data = self._deserialize(row["data"])

        return WorkingMemory(**data)

    # -----------------------------------------------------

    def delete_working(
        self,
        customer_id: str,
    ):

        self.connection.execute(
            """
            DELETE
            FROM working_memory
            WHERE customer_id=?
            """,
            (customer_id,),
        )

        self.connection.commit()

    # =====================================================
    # Episodic Memory
    # =====================================================

    def save_episode(
        self,
        memory: EpisodicMemory,
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO episodic_memory
            (
                customer_id,
                timestamp,
                data
            )
            VALUES (?,?,?)
            """,
            (
                memory.customer_id,
                memory.timestamp.isoformat(),
                self._serialize(memory),
            ),
        )

        self.connection.commit()

    

        # -----------------------------------------------------

    def get_episodes(
        self,
        customer_id: str,
    ) -> list[EpisodicMemory]:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT data
            FROM episodic_memory
            WHERE customer_id=?
            ORDER BY timestamp DESC
            """,
            (customer_id,),
        )


        rows = cursor.fetchall()

        memories: list[EpisodicMemory] = []

        for row in rows:

            data = self._deserialize(row["data"])

            # Support both old and new JSON formats
            if "event" in data:
                event_data = data["event"]
            else:
                event_data = data

            event = Episode(
                event_id=event_data["event_id"],
                event_type=EpisodeType(event_data["event_type"]),
                timestamp=datetime.fromisoformat(
                    event_data["timestamp"]
                ),
                payload=event_data.get("payload", {}),
                metadata=event_data.get("metadata", {}),
            )

            memory = EpisodicMemory(
                customer_id=data["customer_id"],
                event=event,
                importance=data.get("importance", 0.5),
                confidence=data.get("confidence", 1.0),
                access_count=data.get("access_count", 0),
                archived=data.get("archived", False),
                tags=data.get("tags", []),
            )

            memories.append(memory)

        return memories

        

    # -----------------------------------------------------

    def save_episodes(
        self,
        memories: list[EpisodicMemory],
    ):

        for memory in memories:

            self.save_episode(memory)

    # -----------------------------------------------------

    def replace_episodes(
        self,
        customer_id: str,
        memories: list[EpisodicMemory],
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            DELETE
            FROM episodic_memory
            WHERE customer_id=?
            """,
            (customer_id,),
        )

        self.connection.commit()

        self.save_episodes(memories)

    # =====================================================
    # Semantic Memory
    # =====================================================

    def save_semantic(
        self,
        memory: SemanticMemory,
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO semantic_memory
            (
                memory_id,
                customer_id,
                memory_key,
                memory_value,
                data
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                memory.memory_id,
                memory.customer_id,
                memory.key,
                memory.value,
                self._serialize(memory),
            ),
        )

        self.connection.commit()

    # -----------------------------------------------------

    def get_semantic(
        self,
        customer_id: str,
    ) -> list[SemanticMemory]:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT data
            FROM semantic_memory
            WHERE customer_id=?
            ORDER BY memory_key, memory_value
            """,
            (customer_id,),
        )

        rows = cursor.fetchall()

        memories = []

        for row in rows:

            data = self._deserialize(row["data"])

            if isinstance(data.get("created_at"), str):
                data["created_at"] = datetime.fromisoformat(
                    data["created_at"]
                )

            if isinstance(data.get("last_verified"), str):
                data["last_verified"] = datetime.fromisoformat(
                    data["last_verified"]
                )

            memories.append(
                SemanticMemory(**data)
            )

        return memories

    # -----------------------------------------------------

    def save_semantics(
        self,
        memories: list[SemanticMemory],
    ):

        for memory in memories:

            self.save_semantic(memory)

    # -----------------------------------------------------

    def replace_semantic(
        self,
        customer_id: str,
        memories: list[SemanticMemory],
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            DELETE FROM semantic_memory
            WHERE customer_id=?
            """,
            (customer_id,),
        )

        self.connection.commit()

        for memory in memories:

            self.save_semantic(memory)

        # =====================================================
    # Preference Memory
    # =====================================================

    def save_preference(
        self,
        memory: PreferenceMemory,
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO preference_memory
            VALUES (?,?)
            """,
            (
                memory.customer_id,
                self._serialize(memory),
            ),
        )

        self.connection.commit()

    # -----------------------------------------------------

    def get_preference(
        self,
        customer_id: str,
    ) -> Optional[PreferenceMemory]:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT data
            FROM preference_memory
            WHERE customer_id=?
            """,
            (customer_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        data = self._deserialize(row["data"])

        return PreferenceMemory(**data)

    # =====================================================
    # Customer Profile
    # =====================================================

    def save_profile(
        self,
        profile: CustomerProfile,
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO customer_profile
            VALUES (?,?)
            """,
            (
                profile.customer_id,
                self._serialize(profile),
            ),
        )

        self.connection.commit()

    # -----------------------------------------------------

    def get_profile(
        self,
        customer_id: str,
    ) -> Optional[CustomerProfile]:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT data
            FROM customer_profile
            WHERE customer_id=?
            """,
            (customer_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        data = self._deserialize(row["data"])

        # =====================================================
        # Working Memory
        # =====================================================

        if data.get("working_memory"):

            data["working_memory"] = WorkingMemory(
                **data["working_memory"]
            )

        # =====================================================
        # Preference Memory
        # =====================================================

        if data.get("preference_memory"):

            pref = data["preference_memory"]

            if isinstance(pref, dict):

                # Convert datetime strings back
                if isinstance(pref.get("created_at"), str):
                    pref["created_at"] = datetime.fromisoformat(
                        pref["created_at"]
                    )

                if isinstance(pref.get("updated_at"), str):
                    pref["updated_at"] = datetime.fromisoformat(
                        pref["updated_at"]
                    )

                data["preference_memory"] = PreferenceMemory(
                    **pref
                )

        # =====================================================
        # Semantic Memories
        # =====================================================

        semantic = []

        for item in data.get("semantic_memories", []):

            if isinstance(item.get("created_at"), str):
                item["created_at"] = datetime.fromisoformat(
                    item["created_at"]
                )

            if isinstance(item.get("last_verified"), str):
                item["last_verified"] = datetime.fromisoformat(
                    item["last_verified"]
                )

            semantic.append(
                SemanticMemory(**item)
            )

        data["semantic_memories"] = semantic

        # =====================================================
        # Episodic Memories
        # =====================================================

        episodes = []

        for item in data.get("episodic_memories", []):

            #
            # Supports both old and new formats
            #

            if "event" in item:
                event_data = item["event"]
            else:
                event_data = item

            event = Episode(

                event_id=event_data["event_id"],

                event_type=EpisodeType(
                    event_data["event_type"]
                ),

                timestamp=datetime.fromisoformat(
                    event_data["timestamp"]
                ),

                payload=event_data.get(
                    "payload",
                    {},
                ),

                metadata=event_data.get(
                    "metadata",
                    {},
                ),

            )

            episodes.append(

                EpisodicMemory(

                    customer_id=item["customer_id"],

                    event=event,

                    importance=item.get(
                        "importance",
                        0.5,
                    ),

                    confidence=item.get(
                        "confidence",
                        1.0,
                    ),

                    access_count=item.get(
                        "access_count",
                        0,
                    ),

                    archived=item.get(
                        "archived",
                        False,
                    ),

                    tags=item.get(
                        "tags",
                        [],
                    ),

                )

            )

        data["episodic_memories"] = episodes

        # =====================================================
        # Profile Dates
        # =====================================================

        if isinstance(data.get("created_at"), str):

            data["created_at"] = datetime.fromisoformat(
                data["created_at"]
            )

        if isinstance(data.get("updated_at"), str):

            data["updated_at"] = datetime.fromisoformat(
                data["updated_at"]
            )

        # =====================================================
        # Build Customer Profile
        # =====================================================

        return CustomerProfile(**data)

        # -----------------------------------------------------

    def list_profiles(
        self,
    ) -> list[CustomerProfile]:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT data
            FROM customer_profile
            """
        )

        rows = cursor.fetchall()

        profiles = []

        for row in rows:

            data = self._deserialize(row["data"])

            profiles.append(
                CustomerProfile(**data)
            )

        return profiles

    # =====================================================
    # Delete Customer
    # =====================================================

    def delete_customer(
        self,
        customer_id: str,
    ):

        cursor = self.connection.cursor()

        tables = [

            "working_memory",

            "episodic_memory",

            "semantic_memory",

            "preference_memory",

            "customer_profile",

        ]

        for table in tables:

            cursor.execute(

                f"""
                DELETE FROM {table}
                WHERE customer_id=?
                """,

                (customer_id,),

            )

        self.connection.commit()
    


        # =====================================================
    # Repository Health
    # =====================================================

    def health(self) -> dict:

        try:

            cursor = self.connection.cursor()

            cursor.execute("SELECT 1")

            cursor.fetchone()

            return {
                "status": "healthy",
                "database": "sqlite",
            }

        except Exception as ex:

            return {
                "status": "unhealthy",
                "error": str(ex),
            }

    # =====================================================
    # Close Connection
    # =====================================================

    def close(self):

        if self.connection:

            self.connection.close()

    # =====================================================
    # Compatibility Methods
    # =====================================================

    def save_search(self, memory: EpisodicMemory):

        """
        Compatibility wrapper used by SearchService.
        """

        self.save_episode(memory)

    # -----------------------------------------------------

    def get_customer_memory(self, customer_id: str):

        """
        Returns all memory associated with a customer.
        """

        return {

            "working": self.get_working(customer_id),

            "episodes": self.get_episodes(customer_id),

            "semantic": self.get_semantic(customer_id),

            "preferences": self.get_preference(customer_id),

            "profile": self.get_profile(customer_id),

        }

    # -----------------------------------------------------

    def clear(self):

        """
        Clears every table.
        Useful for tests.
        """

        cursor = self.connection.cursor()

        cursor.execute("DELETE FROM working_memory")
        cursor.execute("DELETE FROM episodic_memory")
        cursor.execute("DELETE FROM semantic_memory")
        cursor.execute("DELETE FROM preference_memory")
        cursor.execute("DELETE FROM customer_profile")

        self.connection.commit()

    # -----------------------------------------------------

    def __enter__(self):

        return self

    # -----------------------------------------------------

    def __exit__(

        self,

        exc_type,

        exc,

        tb,

    ):

        self.close()