import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.config import COLLECTION_NAME, PORT
from backend.constants import BOOK_ID_MAP
from backend.llm import generate_answer, generate_answer_with_tools
from backend.models import (
    Book,
    BooksResponse,
    QueryRequest,
    QueryResponse,
    RelevantText,
)
from backend.rag import query_qdrant

logger.remove()
logger.add(
    sink=lambda message: print(message, end=""),  # noqa: T201
    format="{time:YYYY-MM-DD HH:mm:SS} - {level} - {message}",
    level="INFO",
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://eastern-chatbot.nguyenvanloc.com",
        "http://localhost:3000",  # For local development
        "http://127.0.0.1:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check() -> dict[str, str]:
    """Implement the health check endpoint."""
    return {"status": "ok"}


@app.get("/books", response_model=BooksResponse)
async def get_books() -> BooksResponse:
    """Get the list of available books."""
    logger.info("Fetching book list")
    books = [Book(id=book_id, title=title) for book_id, title in BOOK_ID_MAP.items()]
    return BooksResponse(books=books)


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """Query the Qdrant database."""
    logger.info(f"Request: {request}")
    relevant_texts = query_qdrant(
        collection_name=COLLECTION_NAME,
        query=request.query,
        top_k=request.top_k,
        metadata_filter=request.metadata_filter,
    )

    if request.using_tools:
        answer = await generate_answer_with_tools(request.query)
        if not answer:
            answer = "Không tìm thấy thông tin về câu hỏi này"
    else:
        answer = generate_answer(request.query, relevant_texts)
        if not answer:
            answer = "Không tìm thấy thông tin về câu hỏi này"

    return QueryResponse(
        answer=answer,
        relevant_texts=[RelevantText(**text) for text in relevant_texts],
    )


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=PORT, reload=True)  # noqa: S104
