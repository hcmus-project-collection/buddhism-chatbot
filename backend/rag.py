from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue
from sentence_transformers import SentenceTransformer

from backend.config import (COLLECTION_NAME, DEVICE, EMBEDDING_MODEL_NAME,
                            QDRANT_API_KEY, QDRANT_URL)


def connect_to_qdrant() -> QdrantClient:
    """Connect to Qdrant server."""
    if QDRANT_API_KEY:
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return QdrantClient(url=QDRANT_URL)


def embed_query(
    query: str,
    embedding_model: SentenceTransformer | None = None,
) -> list[float]:
    """Embed the query with the embedding model."""
    logger.info(f"Embedding query: {query}")
    embedding_model = embedding_model or SentenceTransformer(
        EMBEDDING_MODEL_NAME,
        device=DEVICE,
    )
    return embedding_model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).tolist()


def query_qdrant(
    query: str,
    client: QdrantClient | None = None,
    top_k: int = 5,
    metadata_filter: dict | None = None,
    collection_name: str = COLLECTION_NAME,
    embedding_model: SentenceTransformer | None = None,
) -> list[dict]:
    """Query Qdrant with a given query."""
    client = client or connect_to_qdrant()

    logger.info(
        f"Querying Qdrant collection '{collection_name}' with query: {query}",
    )

    qdrant_filter = None
    if metadata_filter:
        qdrant_filter = Filter(
            must=[
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value),
                )
                for key, value in metadata_filter.items()
            ],
        )

    query_vector = embed_query(query, embedding_model)

    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
        query_filter=qdrant_filter,
    )

    return [
        {
            "score": r.score,
            "text": r.payload["text"] if r.payload else "",
            "sentence_id": (
                r.payload.get("sentence_id", "") if r.payload else ""
            ),
            "meta": {
                k: v
                for k, v in (r.payload or {}).items()
                if k not in {"text", "sentence_id"}
            },
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
        logger.info(f"\n🔹 Result {i} (score: {r['score']:.4f}):\n{r['text']}")
