import uvicorn
from backend.config import COLLECTION_NAME, PORT
from backend.elastic import connect_to_elasticsearch, search_texts_by_page_info
from fastapi import FastAPI
from backend.llm import generate_answer
from loguru import logger
from pydantic import BaseModel, Field
from backend.rag import connect_to_qdrant, query_qdrant

# Configure loguru to match the existing logging format
logger.remove()  # Remove default handler
logger.add(
    sink=lambda message: print(message, end=""),
    format="{time:YYYY-MM-DD HH:mm:SS} - {level} - {message}",
    level="INFO",
)

qdrant_client = connect_to_qdrant()
elastic_client = connect_to_elasticsearch()

app = FastAPI()


class RelevantText(BaseModel):
    """Relevant text from Qdrant."""

    text: str
    score: float
    sentence_id: str
    meta: dict
    texts_on_the_same_page: list[str]


class QueryRequest(BaseModel):
    """Request body for the query endpoint."""

    query: str
    top_k: int = 5
    metadata_filter: dict[str, str] = Field(default_factory=dict, example={})  # type: ignore


class QueryResponse(BaseModel):
    """Response body for the query endpoint."""

    answer: str
    relevant_texts: list[RelevantText]


@app.get("/")
async def health_check() -> dict[str, str]:
    """Implement the health check endpoint."""
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """Query the Qdrant database."""
    logger.info(f"Request: {request}")
    relevant_texts = query_qdrant(
        client=qdrant_client,
        collection_name=COLLECTION_NAME,
        query=request.query,
        top_k=request.top_k,
        metadata_filter=request.metadata_filter,
    )

    for text in relevant_texts:
        logger.info(f"Processing text: {text}")
        sentence_id = text["sentence_id"]
        if not sentence_id:
            text["texts_on_the_same_page"] = []
            continue
        book_id = text.get("meta", {}).get("book_id", "")
        chapter_id = text.get("meta", {}).get("chapter_id")
        page_id = text.get("meta", {}).get("page_id")
        texts_on_the_same_page = search_texts_by_page_info(
            client=elastic_client,
            book_id=book_id,
            chapter_id=chapter_id,
            page_id=page_id,
        )
        text["texts_on_the_same_page"] = texts_on_the_same_page

    answer = generate_answer(request.query, relevant_texts)

    for text in relevant_texts:
        text["texts_on_the_same_page"] = [
            text["text"] for text in texts_on_the_same_page
        ]

    return QueryResponse(
        answer=answer,
        relevant_texts=[RelevantText(**text) for text in relevant_texts],
    )


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=PORT, reload=True)
