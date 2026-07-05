"""
Product Ingestion Pipeline

Responsibilities
----------------
1. Load master datasets
2. Merge product information
3. Validate products
4. Transform into search documents
5. Upload to Weaviate

No search logic.
No parser.
No repository logic.
"""

from __future__ import annotations

import logging
import time

from agents.ingestion.loader import ProductLoader
from agents.ingestion.transformer import ProductTransformer
from agents.ingestion.validator import ProductValidator
from agents.ingestion.weaviate_writer import WeaviateWriter


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


class ProductIngestionPipeline:

    def __init__(self):

        self.loader = ProductLoader()

        self.transformer = ProductTransformer()

        self.validator = ProductValidator()

        self.writer = WeaviateWriter()

    # ---------------------------------------------------------

    def run(self):

        start = time.perf_counter()

        logging.info("=" * 80)
        logging.info("Starting Product Ingestion Pipeline")
        logging.info("=" * 80)

        try:

            # -------------------------------------------------
            # Step 1
            # -------------------------------------------------

            logging.info("Loading source datasets...")

            data = self.loader.load()

            logging.info(
                "Loaded %d products",
                len(data["products"])
            )

            # -------------------------------------------------
            # Step 2
            # -------------------------------------------------

            logging.info("Joining product metadata...")

            product_documents = self.transformer.transform(data)

            logging.info(
                "Created %d product documents",
                len(product_documents)
            )

            # -------------------------------------------------
            # Step 3
            # -------------------------------------------------

            logging.info("Validating documents...")

            valid_documents = []

            rejected = 0

            for document in product_documents:

                validation = self.validator.validate(document)

                if validation.valid:
                    valid_documents.append(document)
                else:

                    rejected += 1

                    logging.warning(

                        "Rejected Product %s : %s",

                        document.get("product_id"),

                        validation.errors

                    )

            logging.info(

                "Valid Products : %d",

                len(valid_documents)

            )

            logging.info(

                "Rejected Products : %d",

                rejected

            )

            # -------------------------------------------------
            # Step 4
            # -------------------------------------------------

            logging.info("Uploading to Weaviate...")

            inserted = self.writer.write(

                valid_documents

            )

            logging.info(

                "Inserted %d products",

                inserted

            )

            logging.info("Pipeline completed successfully.")

        except Exception:

            logging.exception(

                "Product ingestion failed."

            )

            raise

        finally:

            elapsed = round(

                time.perf_counter() - start,

                2

            )

            logging.info(

                "Execution Time : %.2f sec",

                elapsed

            )

            logging.info("=" * 80)


# ------------------------------------------------------------------


def main():

    ProductIngestionPipeline().run()


# ------------------------------------------------------------------

if __name__ == "__main__":

    main()