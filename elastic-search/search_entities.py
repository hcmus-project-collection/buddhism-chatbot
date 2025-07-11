from elasticsearch import Elasticsearch
from loguru import logger

from utils import connect_to_elasticsearch, ELASTIC_INDEX_NAME


def search_entities_general(
    client: Elasticsearch,
    query: str,
    index_name: str = ELASTIC_INDEX_NAME,
    size: int = 10,
):
    """Search for entities in Elasticsearch."""
    # Query query in this list: text, book_id, chapter_id, page_id, sentence_number
    clauses = [
        {"match": {"text": query}},
        {"match": {"book_id": query}},
        {"match": {"chapter_id": query}},
        {"match": {"page_id": query}},
        {"match": {"sentence_number": query}},
    ]
    query = {"bool": {"should": clauses}}
    response = client.search(index=index_name, body={"query": query, "size": size})
    # return response
    hits = response.get("hits", {}).get("hits", [])
    return [
        {
            "sentence_id": hit["_source"]["sentence_id"],
            "text": hit["_source"]["text"],
            "entity_type": hit["_source"]["entity_type"],
            "entity_value": hit["_source"]["entity_value"],
            "book_id": hit["_source"]["book_id"],
            "chapter_id": hit["_source"]["chapter_id"],
            "page_id": hit["_source"]["page_id"],
            "sentence_number": hit["_source"]["sentence_number"],
            "score": hit.get("_score", 0),
        }
        for hit in hits
    ]


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
    response = client.search(index=index_name, body={"query": query, "size": size})
    hits = response.get("hits", {}).get("hits", [])
    return [
        {
            "sentence_id": hit["_source"]["sentence_id"],
            "text": hit["_source"]["text"],
            "book_id": hit["_source"]["book_id"],
            "chapter_id": hit["_source"]["chapter_id"],
            "page_id": hit["_source"]["page_id"],
            "sentence_number": hit["_source"]["sentence_number"],
            "score": hit.get("_score", 0),
        }
        for hit in hits
    ]


if __name__ == "__main__":
    client = connect_to_elasticsearch()
    results = search_entities_general(client, "RBI_002")
    for result in results:
        logger.info(result)
    book_id = "RBI_002"
    chater_id = "001"
    page_id = "151"
    results = search_texts_by_page_info(client, book_id, chater_id, page_id)
    for result in results:
        logger.info(result)
