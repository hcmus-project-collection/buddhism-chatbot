import asyncio
import json
import os
from datetime import datetime

import json_repair
from dotenv import load_dotenv
from loguru import logger
from openai import AsyncOpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SYSTEM_PROMPT = (
    "Bạn là một chuyên gia ngôn ngữ học và Phật học.\n"
    "Nhiệm vụ của bạn là đánh giá độ tương đồng giữa 2 câu trả lời. Lưu ý rằng "
    "1 trong 2 câu trả lời có thể dài hơn câu còn lại, nên hãy đánh giá độ tương đồng"
    "giữa 2 câu dựa trên nội dung chính của chúng.\n"
    "Hãy trả lời bằng 1 số nguyên từ 1 đến 100, trong đó 1 là không tương đồng và 100 là tương đồng hoàn toàn.\n"
    "Câu trả lời của bạn chỉ bao gồm 1 số nguyên, không kèm thêm bất kỳ lời giải thích nào.\n"
)

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def evaluate_similarity(expected_answer: str, actual_answer: str) -> int:
    """Evaluate the similarity between the expected and actual answers using GPT-4.1 mini."""
    logger.info(f"Evaluating similarity between {expected_answer} and {actual_answer}")
    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"Câu trả lời 1: {expected_answer}\nCâu trả lời 2: {actual_answer}",
            },
        ],
    )
    logger.info(f"Response: {response.choices[0].message.content}")
    try:
        return int(response.choices[0].message.content)
    except ValueError:
        logger.error(
            f"Error evaluating similarity: {response.choices[0].message.content}",
        )
        return await evaluate_similarity(expected_answer, actual_answer)


async def evaluate_json_file(json_file: str) -> list[dict]:
    """Evaluate the similarity between the expected and actual answers using GPT-4.1 mini."""
    with open(json_file, "r") as f:
        data = json_repair.loads(f.read())

    semaphore = asyncio.Semaphore(10)

    async def evaluate_item(item: dict):
        async with semaphore:
            item["gpt_similarity_score"] = await evaluate_similarity(
                item["expected_answer"],
                item["actual_answer"],
            )

    tasks = [evaluate_item(item) for item in data]
    await asyncio.gather(*tasks)
    return data


async def main():
    json_file = "evaluation/results/evaluation_results_20250724_112717.json"
    data = await evaluate_json_file(json_file)
    with open(
        f"evaluation/similarity/gpt_similarity_score_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        "w",
    ) as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())
