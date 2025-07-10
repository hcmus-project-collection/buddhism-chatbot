import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

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


if __name__ == "__main__":
    client = connect_to_elasticsearch()
    print(client.info())
