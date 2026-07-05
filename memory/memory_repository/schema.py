"""memory/schema.py"""

# Placeholder implementation.
"""
memory/schema.py

SQLite schema definitions.
"""

SCHEMA = [

    """
    CREATE TABLE IF NOT EXISTS memory (

        customer_id TEXT NOT NULL,

        memory_type TEXT NOT NULL,

        data TEXT NOT NULL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        PRIMARY KEY (customer_id, memory_type)

    )
    """

]


def create_schema(connection):

    cursor = connection.cursor()

    for statement in SCHEMA:

        cursor.execute(statement)

    connection.commit()