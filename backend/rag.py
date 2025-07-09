import logging
import torch

from sentence_transformers import SentenceTransformer

from qdrant_client import QdrantClient

from config import EMBEDDING_MODEL_NAME, QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)
model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)


def connect_to_qdrant() -> QdrantClient:
    """Connect to Qdrant server."""
    if QDRANT_API_KEY:
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return QdrantClient(url=QDRANT_URL)


def embed_query(query: str) -> list[float]:
    """Embed the query with the embedding model."""
    logger.info(f"Embedding query: {query}")
    return model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).tolist()


def query_qdrant(
    client: QdrantClient,
    collection_name: str,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """Query Qdrant with a given query."""
    logger.info(
        f"Querying Qdrant collection '{collection_name}' with query: {query}",
    )
    query = embed_query(query)

    results = client.search(
        collection_name=collection_name,
        query_vector=query,
        limit=top_k,
        with_payload=True,
    )

    return [
        {
            "score": r.score,
            "text": r.payload["text"],
            "sentence_id": r.payload.get("sentence_id", ""),
            "meta": {k: v for k, v in r.payload.items() if k not in {"text", "sentence_id"}}
        }
        for r in results
    ]


if __name__ == "__main__":
    client = connect_to_qdrant()
    user_query = "Đế Quân dạy điều gì về nhân quả?"
    results = query_qdrant(
        client=client,
        collection_name=COLLECTION_NAME,
        query=user_query,
        top_k=5,
    )

    for i, r in enumerate(results, 1):
        print(f"\n🔹 Result {i} (score: {r['score']:.4f}):\n{r['text']}")
