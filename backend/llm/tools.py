import sys
from pathlib import Path
from typing import Literal

# Add the project root to Python path so we can import backend modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastmcp import FastMCP
from loguru import logger

from backend.constants import Title, Volume
from backend.rag import query_qdrant
from backend.elastic import search_texts_by_page_info

mcp = FastMCP("Eastern Religion Retriever")


@mcp.tool()
def retrieve_text(
    query: str,
    title: Literal[
        Title.AN_SI_TOAN_THU,
        Title.KINH_TUONG_UNG_BO,
        Title.QUAN_AM_THI_KINH,
        Title.THIEN_UYEN_TAP_ANH,
    ]
    | str
    | None = None,
) -> list[dict]:
    """Retrieve text from the database.

    Args:
        query: The query to retrieve text from the database.
        title: The title of the book to retrieve. Carefully choosing this
        value, only define it the user prompt is specific, or needs to confirm
        with user first.

    """
    logger.info(f"Calling retrieve_text tool with arguments: {query}, {title}")
    if not title:
        results = query_qdrant(query)

    if isinstance(title, Title):
        title = title.value

    metadata_filter = {
        "title": title,
    }
    results = query_qdrant(query, metadata_filter=metadata_filter)

    for result in results:
        logger.info(f"Processing text")
        sentence_id = result["sentence_id"]
        if not sentence_id:
            result["texts_on_the_same_page"] = []
            continue
        book_id = result.get("meta", {}).get("book_id", "")
        chapter_id = result.get("meta", {}).get("chapter_id")
        page_id = result.get("meta", {}).get("page_id")
        texts_on_the_same_page = search_texts_by_page_info(
            book_id=book_id,
            chapter_id=chapter_id,
            page_id=page_id,
        )
        result["texts_on_the_same_page"] = texts_on_the_same_page

    return results


@mcp.tool()
def filter_by_volume(
    query: str,
    volume: Literal[
        Volume.AN_SI_TOAN_THU_QUYEN_I,
        Volume.AN_SI_TOAN_THU_QUYEN_II,
        Volume.AN_SI_TOAN_THU_QUYEN_III,
        Volume.AN_SI_TOAN_THU_QUYEN_IV,
    ],
) -> list[dict]:
    """Filter the text by volume.

    Args:
        query: The query to retrieve text from the database.
        volume: The volume of the book to retrieve. This tool is used only for
        'An Sĩ Toàn Thư' book. Use only when user explicitly asks for a
        specific volume.

    """
    logger.info(
        f"Calling filter_by_volume tool with arguments: {query}, {volume}",
    )
    return query_qdrant(
        query,
        metadata_filter={
            "volume": volume,
        },
    )


if __name__ == "__main__":
    mcp.run()
