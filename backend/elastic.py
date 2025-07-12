from backend.config import (
    ELASTIC_HOST,
    ELASTIC_INDEX_NAME,
    ELASTIC_PASSWORD,
    ELASTIC_PORT,
    ELASTIC_USERNAME,
)
from elasticsearch import Elasticsearch
from loguru import logger


def connect_to_elasticsearch() -> Elasticsearch:
    """Connect to Elasticsearch."""
    return Elasticsearch(
        hosts=[f"https://{ELASTIC_HOST}:{ELASTIC_PORT}"],
        http_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
        verify_certs=False,
    )


def search_texts_by_page_info(
    client: Elasticsearch,
    book_id: str | None = None,
    chapter_id: str | None = None,
    page_id: str | None = None,
    index_name: str = ELASTIC_INDEX_NAME,
    size: int = 10,
):
    clauses = []
    if book_id:
        clauses.append({"match": {"book_id": book_id}})
    if chapter_id:
        clauses.append({"match": {"chapter_id": chapter_id}})
    if page_id:
        clauses.append({"match": {"page_id": page_id}})
    query = {"bool": {"should": clauses}}
    response = client.search(
        index=index_name,
        body={"query": query, "size": size},
    )
    hits = response.get("hits", {}).get("hits", [])
    results = {}
    for hit in hits:
        source = hit["_source"]
        score = hit.get("_score", 0)
        sentence_id = source["sentence_id"]

        doc = {
            "sentence_id": sentence_id,
            "text": source["text"],
            "book_id": source["book_id"],
            "chapter_id": source["chapter_id"],
            "page_id": source["page_id"],
            "sentence_number": source["sentence_number"],
            "score": score,
        }

        # Keep only the result with the highest score for each sentence_id
        if sentence_id not in results or score > results[sentence_id]["score"]:
            results[sentence_id] = doc

    results = sorted(results.values(), key=lambda x: x["sentence_id"])

    logger.info(f"Elasticsearch results: {results}")

    return results
