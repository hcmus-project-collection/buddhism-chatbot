import logging
import os

import openai

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()

OPENAI_API_BASE = os.getenv(
    "OPENAI_API_BASE",
    "https://api.openai.com/v1",
)  # In case we need to use a different OpenAI-compatible API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "no-need")
OPENAI_MODEL_NAME = os.getenv(
    "OPENAI_MODEL_NAME",
    "gpt-4o-mini",
)

client = openai.OpenAI(
    base_url=OPENAI_API_BASE,
    api_key=OPENAI_API_KEY,
)

SYSTEM_PROMPT = """
Bạn là một chuyên gia trong lĩnh vực tôn giáo phương Đông.

Bạn sẽ được cung cấp câu hỏi (question), các nội dung liên quan (relevant texts) (nếu có), và hướng dẫn (instruction).

Bạn sẽ dựa vào các nội dung liên quan (relevant texts) và hướng dẫn (instruction) để trả lời câu hỏi (question).

Nếu câu hỏi không liên quan đến tôn giáo phương Đông (như giá BTC hôm nay bao nhiêu, Python là gì, ...), hãy trả lời một cách lịch sự rằng câu hỏi này không liên quan đến lĩnh vực chuyên môn của bạn.

Nếu nội dung liên quan không được tìm thấy (là rỗng hoặc không có), hãy trả lời câu hỏi một cách lịch sự rằng bạn không có thông tin về câu hỏi này từ kho ngữ liệu.
""".strip()

USER_PROMPT_TEMPLATE = """
Câu hỏi: {question}

Các nội dung liên quan:
{relevant_texts}

Hướng dẫn: hãy dựa trên các nội dung liên quan để trả lời câu hỏi.

""".strip()


def generate_answer(
    question: str,
    relevant_texts: str | list[str],
    model_name: str = OPENAI_MODEL_NAME,
) -> str:
    if isinstance(relevant_texts, list):
        relevant_texts = "\n".join(f"- {text}" for text in relevant_texts)

    prompt = USER_PROMPT_TEMPLATE.format(
        question=question,
        relevant_texts=relevant_texts,
    )
    logger.info(f"Calling LLM at {OPENAI_API_BASE} with model {model_name}")
    logger.info(f"Prompt: {prompt}")
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return ""

    return response.choices[0].message.content or ""


if __name__ == "__main__":
    retrieved = [
        "Người làm thiện được phúc, người làm ác chịu báo ứng.",
        "Đế Quân dạy rằng nhân quả không sai một mảy may.",
    ]
    question = "Đế Quân dạy điều gì về nhân quả?"
    response = generate_answer(question, retrieved)
    logger.info(f"🤖 LLM said that: {response}")
