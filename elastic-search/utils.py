import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from loguru import logger

load_dotenv()

ELASTIC_HOST = os.getenv("ELASTIC_HOST")
ELASTIC_PORT = os.getenv("ELASTIC_PORT")
ELASTIC_USERNAME = os.getenv("ELASTIC_USERNAME")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
ELASTIC_INDEX_NAME = os.getenv("ELASTIC_INDEX_NAME")


def connect_to_elasticsearch() -> Elasticsearch:
    """Connect to Elasticsearch."""
    return Elasticsearch(
        hosts=[f"https://{ELASTIC_HOST}:{ELASTIC_PORT}"],
        http_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
        verify_certs=False,
    )


def recreate_index(client: Elasticsearch, index_name: str) -> None:
    """Delete and re-create the Elasticsearch index."""
    if client.indices.exists(index=index_name):
        logger.warning(f"Index '{index_name}' already exists. Deleting it...")
        client.indices.delete(index=index_name)
        logger.info(f"Deleted index '{index_name}'")

    mapping = {
        "mappings": {
            "properties": {
                "sentence_id": {"type": "keyword"},
                "text": {"type": "text"},
                "entity_type": {"type": "keyword"},
                "entity_value": {"type": "text"},
            },
        },
    }

    client.indices.create(index=index_name, body=mapping)
    logger.info(f"Created new index '{index_name}' with mapping.")


if __name__ == "__main__":
    client = connect_to_elasticsearch()
