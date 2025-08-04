from pydantic import BaseModel, Field


class RelevantText(BaseModel):
    """Relevant text from Qdrant."""

    text: str
    score: float
    book_id: str
    chapter_id: str
    page: str


class QueryRequest(BaseModel):
    """Request body for the query endpoint."""

    query: str
    top_k: int = 5
    metadata_filter: dict[str, str] = Field(default_factory=dict, json_schema_extra={"example": {}})  # type: ignore
    using_tools: bool = False


class QueryResponse(BaseModel):
    """Response body for the query endpoint."""

    answer: str
    relevant_texts: list[RelevantText]


class Book(BaseModel):
    """Book information."""

    id: str
    title: str


class BooksResponse(BaseModel):
    """Response body for the books endpoint."""

    books: list[Book]


class FunctionCall(BaseModel):
    """Representation of a function call."""

    name: str
    arguments: str | dict


class ToolCall(BaseModel):
    """Representation of a tool call."""

    id: str
    function: FunctionCall
