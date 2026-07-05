"""
Weaviate Writer

Responsibilities
----------------
1. Connect to Weaviate
2. Batch insert product documents
3. Upsert existing products
4. Close connection

No CSV loading.
No validation.
No transformations.
"""

from __future__ import annotations

import logging
import uuid

import weaviate
from weaviate.util import generate_uuid5

from config.search_config import COLLECTION_NAME


class WeaviateWriter:

    def __init__(self):

        self.client = weaviate.connect_to_local()

        self.collection = self.client.collections.get(
            COLLECTION_NAME
        )

    # ---------------------------------------------------------

    def write(
        self,
        documents: list[dict]
    ) -> int:

        inserted = 0

        try:

            with self.collection.batch.dynamic() as batch:

                for document in documents:

                    try:

                        product_uuid = generate_uuid5(
                            document["product_id"]
                        )

                        batch.add_object(

                            properties=document,

                            uuid=product_uuid

                        )

                        inserted += 1

                    except Exception:

                        logging.exception(

                            "Failed inserting product %s",

                            document.get("product_id")

                        )

        except Exception:

            logging.exception(

                "Batch upload failed."

            )

            raise

        return inserted

    # ---------------------------------------------------------

    def delete_all(self):

        """
        Delete all products.

        Useful for rebuilding the search index.
        """

        self.collection.data.delete_many()

    # ---------------------------------------------------------

    def count(self):

        """
        Returns approximate object count.
        """

        aggregate = self.collection.aggregate.over_all()

        return aggregate.total_count

    # ---------------------------------------------------------

    def close(self):

        self.client.close()

    # ---------------------------------------------------------

    def __enter__(self):

        return self

    # ---------------------------------------------------------

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb
    ):

        self.close()