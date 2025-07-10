import logging

import uvicorn

from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL_NAME, DEVICE, PORT, COLLECTION_NAME
from llm import generate_answer
from rag import query_qdrant, connect_to_qdrant

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=DEVICE)

qdrant_client = connect_to_qdrant()

app = FastAPI()


class RelevantText(BaseModel):
    """Relevant text from Qdrant."""
    text: str
    score: float
    sentence_id: str
    meta: dict

class QueryRequest(BaseModel):
    """Request body for the query endpoint."""

    query: str
    top_k: int = 5
    metadata_filter: dict[str, str] | None = None


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
    relevant_texts = query_qdrant(
        client=qdrant_client,
        collection_name=COLLECTION_NAME,
        query=request.query,
        top_k=request.top_k,
        embedding_model=embedding_model,
        metadata_filter=request.metadata_filter,
    )
    answer = generate_answer(request.query, relevant_texts)
    return QueryResponse(
        answer=answer,
        relevant_texts=[
            RelevantText(**text) for text in relevant_texts
        ],
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
