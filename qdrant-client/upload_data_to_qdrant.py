import json
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from tqdm import tqdm

load_dotenv()

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "eastern_religion")
EMBEDDING_DIM = int(
    os.getenv("EMBEDDING_DIM", 768),
)  # match the embedding model intfloat/multilingual-e5-base
BATCH_SIZE = 256
BASE_JSONL_EMBEDDINGS_DIR = Path("./jsonl/embeddings")


def connect_to_qdrant() -> QdrantClient:
    """Connect to Qdrant server."""
    if QDRANT_API_KEY:
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return QdrantClient(url=QDRANT_URL)


def create_collection(
    client: QdrantClient,
    collection_name: str,
    force_recreate: bool = False,
    embedding_dim: int = EMBEDDING_DIM,
    distance: Distance = Distance.COSINE,
) -> None:
    """Create a collection in Qdrant."""
    vectors_config = VectorParams(size=embedding_dim, distance=distance)
    if force_recreate:
        client.recreate_collection(
            collection_name,
            vectors_config=vectors_config,
        )
    else:
        try:
            client.create_collection(
                collection_name,
                vectors_config=vectors_config,
            )
        except Exception as e:
            logger.warning(
                f"Collection '{collection_name}' already exists or "
                f"could not be created: {e}",
            )


def flatten_entities(meta: dict) -> dict:
    """Flatten NER entity types for filtering."""
    flat = {}
    entities = meta.get("entities", [])
    for ent in entities:
        ent_type = ent.get("type")
        ent_text = ent.get("text")
        if ent_type and ent_text:
            key = f"entities_{ent_type}"
            flat.setdefault(key, []).append(ent_text)
    return flat


def load_points_from_jsonl(file_path: str | Path) -> list[PointStruct]:
    """Load points from a JSONL file and enrich metadata."""
    points = []
    if isinstance(file_path, str):
        file_path = Path(file_path)
    with file_path.open("r", encoding="utf-8") as f:
        for line in tqdm(f, desc=f"Loading points from {file_path.name}"):
            data = json.loads(line)
            page_id = data["metadata"]["page_id"]
            # Extract structured metadata from sentence_id
            try:
                book_id, chapter_id, page = page_id.split(".")
            except ValueError:
                book_id = chapter_id = page = None
                logger.warning(f"Malformed page_id: {page_id}")

            payload = {
                "text": data["text"],
                "page_id": page_id,
                "book_id": book_id,
                "chapter_id": chapter_id,
                "page": page,
                **data.get("meta", {}),
            }

            point = PointStruct(
                id=uuid.uuid4().hex,  # Generate a unique ID for each point
                vector=data["embedding"],
                payload=payload,
            )
            points.append(point)
    logger.info(f"Loaded {len(points)} points from {file_path.name}")
    return points


def upload_data_to_qdrant(
    client: QdrantClient,
    collection_name: str,
    points: list[PointStruct],
    batch_size: int = BATCH_SIZE,
    force_recreate_collection: bool = False,
) -> None:
    """Upload points to Qdrant in batches."""
    create_collection(
        client,
        collection_name,
        force_recreate=force_recreate_collection,
    )

    for i in tqdm(range(0, len(points), batch_size), desc="Uploading points"):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=collection_name,
            points=batch,
        )
    logger.info(
        f"Uploaded {len(points)} points to collection '{collection_name}'",
    )


def main() -> None:
    """Implement the main function to upload data to Qdrant."""
    client = connect_to_qdrant()
    logger.info(f"Connected to Qdrant at {QDRANT_URL}")

    collection_name = COLLECTION_NAME
    force_recreate = (
        os.getenv("QDRANT_FORCE_RECREATE", "false").lower() == "true"
    )
    logger.info(
        f"Using collection '{collection_name}' with "
        f"force_recreate={force_recreate}",
    )

    json_files = list(BASE_JSONL_EMBEDDINGS_DIR.glob("*.jsonl"))
    logger.info(
        f"Processing {len(json_files)} JSONL files in "
        f"{BASE_JSONL_EMBEDDINGS_DIR}",
    )
    all_points = []
    for json_file in json_files:
        logger.info(f"Loading points from {json_file.name}")
        points = load_points_from_jsonl(json_file)
        all_points.extend(points)
    logger.info(f"Total points loaded: {len(all_points)}")

    if not all_points:
        logger.warning("No points to upload. Exiting.")
        return

    upload_data_to_qdrant(
        client,
        collection_name,
        all_points,
        batch_size=BATCH_SIZE,
        force_recreate_collection=force_recreate,
    )


if __name__ == "__main__":
    main()
