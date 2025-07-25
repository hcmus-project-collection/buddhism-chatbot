import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

import json_repair
from dotenv import load_dotenv
from loguru import logger
from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from bert_score import score

load_dotenv()

# Initialize logging
logger.add(f"evaluate_answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SYSTEM_PROMPT = (
    "Bạn là một chuyên gia ngôn ngữ học và Phật học.\n"
    "Nhiệm vụ của bạn là đánh giá độ tương đồng giữa 2 câu trả lời. Lưu ý rằng "
    "1 trong 2 câu trả lời có thể dài hơn câu còn lại, nên hãy đánh giá độ tương đồng"
    "giữa 2 câu dựa trên nội dung chính của chúng.\n"
    "Hãy trả lời bằng 1 số nguyên từ 1 đến 100, trong đó 1 là không tương đồng và 100 là tương đồng hoàn toàn.\n"
    "Câu trả lời của bạn chỉ bao gồm 1 số nguyên, không kèm thêm bất kỳ lời giải thích nào.\n"
)

# Initialize models
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
sentence_model = SentenceTransformer("intfloat/e5-base")


class AnswerEvaluator:
    """Unified answer evaluator with multiple evaluation methods."""

    def __init__(self):
        self.openai_client = openai_client
        self.sentence_model = sentence_model

    async def evaluate_similarity_openai(self, expected_answer: str, actual_answer: str) -> int:
        """Evaluate the similarity between the expected and actual answers using GPT-4.1 mini."""
        if not self.openai_client:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")

        logger.info(f"Evaluating OpenAI similarity between {expected_answer} and {actual_answer}")

        response = await self.openai_client.chat.completions.create(
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

        logger.info(f"OpenAI Response: {response.choices[0].message.content}")

        try:
            return int(response.choices[0].message.content)
        except ValueError:
            logger.error(
                f"Error evaluating OpenAI similarity: {response.choices[0].message.content}",
            )
            return await self.evaluate_similarity_openai(expected_answer, actual_answer)

    def evaluate_similarity_cosine(self, expected_answer: str, actual_answer: str) -> float:
        """Calculate the cosine similarity between the expected and actual answers."""
        logger.info(f"Calculating cosine similarity between {expected_answer} and {actual_answer}")

        expected_embedding = self.sentence_model.encode(expected_answer, normalize_embeddings=True)
        actual_embedding = self.sentence_model.encode(actual_answer, normalize_embeddings=True)

        # Reshape embeddings to 2D arrays for cosine_similarity
        expected_embedding = expected_embedding.reshape(1, -1)
        actual_embedding = actual_embedding.reshape(1, -1)

        similarity = cosine_similarity(expected_embedding, actual_embedding)
        logger.info(f"Cosine similarity: {similarity}")
        return float(similarity[0][0])  # Extract the scalar value and convert to Python float

    def evaluate_similarity_bert(self, expected_answer: str, actual_answer: str) -> float:
        """Calculate the BERT score between the expected and actual answers."""
        logger.info(f"Calculating BERT score between {expected_answer} and {actual_answer}")

        # BERT score expects lists of candidates and references
        bert_score = score([actual_answer], [expected_answer], lang="vi")
        # Extract F1 score (third element) from the tuple
        f1_score = bert_score[2].item()  # Convert tensor to float
        logger.info(f"BERT score: {f1_score}")
        return float(f1_score)

    def load_json_data(self, json_file: str) -> List[Dict]:
        """Load and parse JSON data from file."""
        logger.info(f"Loading data from {json_file}")
        with open(json_file, "r") as f:
            data = json_repair.loads(f.read())
        return data

    def save_json_data(self, data: List[Dict], output_file: str) -> None:
        """Save data to JSON file."""
        logger.info(f"Saving data to {output_file}")
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    async def evaluate_json_file_openai(self, json_file: str, max_concurrent: int = 10) -> List[Dict]:
        """Evaluate the similarity between expected and actual answers using OpenAI GPT."""
        data = self.load_json_data(json_file)
        semaphore = asyncio.Semaphore(max_concurrent)

        async def evaluate_item(item: Dict):
            async with semaphore:
                item["gpt_similarity_score"] = await self.evaluate_similarity_openai(
                    item["expected_answer"],
                    item["actual_answer"],
                )

        tasks = [evaluate_item(item) for item in data]
        await asyncio.gather(*tasks)
        return data

    def evaluate_json_file_cosine(self, json_file: str) -> List[Dict]:
        """Evaluate the similarity using cosine similarity."""
        data = self.load_json_data(json_file)

        for item in data:
            item["cosine_similarity"] = self.evaluate_similarity_cosine(
                item["expected_answer"],
                item["actual_answer"],
            )
        return data

    def evaluate_json_file_bert(self, json_file: str) -> List[Dict]:
        """Evaluate the similarity using BERT score."""
        data = self.load_json_data(json_file)

        for item in data:
            item["bert_score"] = self.evaluate_similarity_bert(
                item["expected_answer"],
                item["actual_answer"],
            )
        return data

    async def evaluate_json_file_all(self, json_file: str, max_concurrent: int = 10) -> List[Dict]:
        """Evaluate using all available methods."""
        logger.info("Starting evaluation with all methods")

        # Start with cosine similarity (fastest)
        data = self.evaluate_json_file_cosine(json_file)
        logger.info("Completed cosine similarity evaluation")

        # Add BERT scores
        for item in data:
            item["bert_score"] = self.evaluate_similarity_bert(
                item["expected_answer"],
                item["actual_answer"],
            )
        logger.info("Completed BERT score evaluation")

        # Add OpenAI scores if available
        if self.openai_client:
            semaphore = asyncio.Semaphore(max_concurrent)

            async def evaluate_item_openai(item: Dict):
                async with semaphore:
                    item["gpt_similarity_score"] = await self.evaluate_similarity_openai(
                        item["expected_answer"],
                        item["actual_answer"],
                    )

            tasks = [evaluate_item_openai(item) for item in data]
            await asyncio.gather(*tasks)
            logger.info("Completed OpenAI evaluation")
        else:
            logger.warning("OpenAI API key not available, skipping OpenAI evaluation")

        return data


async def main():
    """Main function to run evaluation."""
    evaluator = AnswerEvaluator()

    # Configuration
    json_file = "evaluation/results/evaluation_results_20250724_112717.json"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Evaluate with all methods
    data = await evaluator.evaluate_json_file_all(json_file)

    # Save combined results
    output_file = f"evaluation/similarity/all_similarities_{timestamp}.json"
    evaluator.save_json_data(data, output_file)

    logger.info(f"Evaluation completed. Results saved to {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
