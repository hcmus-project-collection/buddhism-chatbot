import json
import os
import re
import time
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

import json_repair
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from datasets import Dataset
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

logger.add(f"evaluation/test_dataset/create_dataset_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

AZURE_INFERENCE_SDK_ENDPOINT=os.getenv("AZURE_INFERENCE_SDK_ENDPOINT")
AZURE_INFERENCE_SDK_MODEL_NAME=os.getenv("AZURE_INFERENCE_SDK_MODEL_NAME")
AZURE_INFERENCE_SDK_KEY=os.getenv("AZURE_INFERENCE_SDK_KEY")

CHUNK_SIZE = 500
SKIP_SIZE = 3000
MAX_QUESTIONS_PER_CHUNK = 3
MAX_QUESTIONS_PER_FILE = 200
NUMBER_OF_QUESTIONS = 1000
SKIPPED_MARKDOWN_FILES = ["Am Chat Giai Am (NXB Ha Noi 1922) - Mac Dinh Tu_ 84 Trang.md"]

SOURCE_DIR = "docling/pdfs"
markdown_files = [file for file in Path(SOURCE_DIR).glob("*.md")]

client = ChatCompletionsClient(
    endpoint=AZURE_INFERENCE_SDK_ENDPOINT,
    credential=AzureKeyCredential(AZURE_INFERENCE_SDK_KEY),
    api_version="2024-05-01-preview",
)
SYSTEM_PROMPT = (
    "You are a Buddhist scholar.\n"
    "Based on the given passage, generate up to "
    f"{MAX_QUESTIONS_PER_CHUNK} question-answer pairs for evaluation of a chatbot.\n"
    "The questions should be answerable from the passage only.\n"
    "Format your output strictly as a JSON list like this:\n"
    "[{\"question\": \"...\", \"answer\": \"...\"}, ...]\n"
    "Do not include any other text in your response.\n"
    "The question and answer should be in Vietnamese.\n"
)

OUTPUT_PATH = "evaluation/test_dataset/test_set.json"


def _read_markdown_files(files: list[Path] = markdown_files) -> str:
    """Read Markdown files and return the combined text."""
    combined_text = ""
    for file_path in files:
        content = Path(file_path).read_text(encoding="utf-8")
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)  # Remove HTML comments
        content = re.sub(r"\n{2,}", "\n\n", content)
        combined_text += content.strip() + "\n\n"
    return combined_text


def _split_text_into_chunks(text: str, chunk_size: int = CHUNK_SIZE) -> Generator[str, None, None]:
    """Split text into chunks of a given size."""
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]


def _generate_questions(text: str) -> list[dict]:
    """Generate questions from text."""
    logger.info(f"Generating questions for {text[:100]}...")
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        UserMessage(content=f"The passage is: {text}"),
    ]
    try:
        response = client.complete(
            messages=messages,
            model=AZURE_INFERENCE_SDK_MODEL_NAME,
        )
    except HttpResponseError as e:
        logger.error(f"Error generating questions: {e}")
        return []

    formatted_response = (
        response.choices[0].message.content
        .replace("```json", "")
        .replace("```", "")
    )
    logger.info(f"Model response: {formatted_response}")
    return json_repair.loads(formatted_response)


def generate_test_set(
    number_of_questions: int = NUMBER_OF_QUESTIONS,
    max_questions_per_file: int = MAX_QUESTIONS_PER_FILE,
    output_file: str = OUTPUT_PATH,
) -> list[dict]:
    """Generate a test set of questions and answers."""
    questions_pairs = []
    for file in markdown_files:
        if file.name in SKIPPED_MARKDOWN_FILES:
            continue
        logger.info(f"Processing {file.name}...")
        file_questions_pairs = []

        text = _read_markdown_files([file])
        text = text[SKIP_SIZE:]

        for chunk in _split_text_into_chunks(text):
            questions = _generate_questions(chunk)
            questions_pairs.extend(questions)
            file_questions_pairs.extend(questions)

            logger.info(f"Generated {len(questions_pairs)} questions so far...")

            if (
                len(questions_pairs) >= number_of_questions
                or len(file_questions_pairs) >= max_questions_per_file
            ):
                break

            time.sleep(1)  # To avoid rate limiting

    with open(output_file, "w") as f:
        json.dump(questions_pairs, f, ensure_ascii=False)

    return questions_pairs

if __name__ == "__main__":
    # question_pairs = generate_test_set()
    with open(OUTPUT_PATH, "r") as f:
        question_pairs = json.load(f)
    dataset = Dataset.from_list(question_pairs)
    dataset.push_to_hub("vanloc1808/buddhist-scholar-test-set")
