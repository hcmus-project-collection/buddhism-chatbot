import json
import re

from pathlib import Path
from loguru import logger

CLEANED_JSONL_DIR = Path("jsonl/cleaned")
CLEANED_JSONL_DIR.mkdir(exist_ok=True)


def clean_text(text: str) -> str:
    # 1. Remove excessive whitespace and line breaks
    text = re.sub(r"\s+", " ", text.strip())

    # 2. Normalize punctuation
    text = re.sub(r"[“”]", '"', text)  # curly double quotes → straight
    text = re.sub(r"[‘’]", "'", text)  # curly single quotes → straight
    text = re.sub(r"[–—]", "-", text)  # dashes → hyphen

    return text


def clean_jsonl(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as fin, open(
        output_path, "w", encoding="utf-8"
    ) as fout:
        for line in fin:
            record = json.loads(line)
            if "text" in record:
                record["text"] = clean_text(record["text"])
            fout.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info(f"✅ Cleaned file saved to: {output_path}")


def main():
    json_files = list(Path("jsonl/raw").glob("*.jsonl"))
    for json_file in json_files:
        clean_jsonl(
            json_file,
            CLEANED_JSONL_DIR / json_file.name.replace("_with_ner", ""),
        )


if __name__ == "__main__":
    main()
