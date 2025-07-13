import openai
import os

from backend.llm.constants import MCP_SERVER_PATH
from backend.llm.utils import call_and_return_tool_result
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

SYSTEM_PROMPT = """
Bạn là một chuyên gia trả lời câu hỏi về tôn giáo phương Đông.

Bạn sẽ được cung cấp tools để query câu hỏi từ user và trả ra kết quả.

Tool sẽ trả ra cho bạn các nội dung có similarity cao với câu hỏi.

Bạn cần dựa vào các nội dung này để trả lời câu hỏi.

Nếu câu hỏi không liên quan đến tôn giáo phương Đông (như giá BTC hôm nay bao nhiêu, Python là gì, ...), hãy trả lời một cách lịch sự rằng câu hỏi này không liên quan đến lĩnh vực chuyên môn của bạn.

Nếu nội dung liên quan không được tìm thấy (là rỗng hoặc không có), hãy trả lời câu hỏi một cách lịch sự rằng bạn không có thông tin về câu hỏi này từ kho ngữ liệu.

"""


async def generate_answer_with_tools(question: str) -> str:
    """Generate answer with tools."""
    openai_client = openai.AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": question,
        },
    ]
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    assistant_message = response.choices[0].message
    while assistant_message.tool_calls:
        results = await call_and_return_tool_result(
            tools=assistant_message.tool_calls,
            mcp_server_path=MCP_SERVER_PATH,
        )
        messages.extend(results)
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        assistant_message = response.choices[0].message
    logger.info(f"Assistant message: {assistant_message.content}")
    return assistant_message.content


if __name__ == "__main__":
    import asyncio

    asyncio.run(generate_answer_with_tools("Đế Quân dạy điều gì về nhân quả?"))
