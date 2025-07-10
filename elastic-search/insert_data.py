import json
import logging
from pathlib import Path

from elasticsearch import Elasticsearch
from tqdm import tqdm

from utils import connect_to_elasticsearch, ELASTIC_INDEX_NAME

BASE_JSONL_DIR = Path("./jsonl/cleaned")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _normalize_entities(entities: dict) -> dict:
    """Normalize entities from semicolon-separated to list of strings.

    Before normalization:
        {"PER": "Bồ Đề Đạt Ma; Bodhidharma", "LOC": "Trung Quốc"}

    After normalization:
        {"PER": ["Bồ Đề Đạt Ma", "Bodhidharma"], "LOC": ["Trung Quốc"]}
    """
    normalized_entities = {}
    for key, values in entities.items():
        logger.info(f"Normalizing entities for {key}: {values}")
        normalized_entities[key] = [
            value.strip() for value in values[0].split(";")
        ]
        logger.info(f"Normalized entities for {key}: {normalized_entities[key]}")
    return normalized_entities


def extract_entities_from_jsonl(jsonl_file: str | Path):
    """Extract NER entities from a JSONL file."""
    if isinstance(jsonl_file, str):
        jsonl_file = Path(jsonl_file)
    with jsonl_file.open("r", encoding="utf-8") as f:
        for line in tqdm(f, desc=f"Extracting entities from {jsonl_file.name}"):
            obj = json.loads(line)
            entities = obj.get("entities", {})
            if not entities:
                continue
            sentence_id = obj["id"]
            entities = _normalize_entities(entities)
            for entity_type, entity_values in entities.items():
                for entity_value in entity_values:
                    yield {
                        "_index": ELASTIC_INDEX_NAME,
                        "_id": f"{sentence_id}_{entity_type}_{entity_value}",
                        "_source": {
                            "sentence_id": sentence_id,
                            "text": obj["text"],
                            "entity_type": entity_type,
                            "entity_value": entity_value,
                        },
                    }


def index_named_entities(
    client: Elasticsearch,
    jsonl_dir: str | Path,
):
    """Index named entities into Elasticsearch with logging and progress."""
    if isinstance(jsonl_dir, str):
        jsonl_dir = Path(jsonl_dir)

    jsonl_files = list(jsonl_dir.glob("*.jsonl"))
    logger.info(f"Found {len(jsonl_files)} JSONL files in {jsonl_dir}")

    for jsonl_file in jsonl_files:
        logger.info(f"Processing file: {jsonl_file.name}")
        entity_docs = list(extract_entities_from_jsonl(jsonl_file))
        if not entity_docs:
            logger.warning(f"No entities found in {jsonl_file.name}")
            continue

        for doc in tqdm(
            entity_docs,
            desc=f"Indexing entities from {jsonl_file.name}",
            total=len(entity_docs),
        ):
            try:
                client.index(
                    index=doc["_index"],
                    id=doc["_id"],
                    document=doc["_source"],
                )
            except Exception as e:
                logger.error(f"Failed to index doc {doc['_id']}: {e}")


if __name__ == "__main__":
    logger.info("Connecting to Elasticsearch...")
    client = connect_to_elasticsearch()
    logger.info("Connected.")
    index_named_entities(client=client, jsonl_dir=BASE_JSONL_DIR)
