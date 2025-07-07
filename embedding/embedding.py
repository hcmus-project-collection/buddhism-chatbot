# Ensure to run this yourself, because the output of embedding for kinhtuongungbo.jsonl is 512MB, so I cannot push it to GitHub.
import json
import logging
import torch

from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)

BASE_CLEANED_JSONL_PATH = Path("jsonl/cleaned")
EMBEDDING_JSONL_PATH = Path("jsonl/embeddings")
EMBEDDING_JSONL_PATH.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "intfloat/multilingual-e5-base"
BATCH_SIZE = 32

logger.info(f"Loading model: {MODEL_NAME} on device: {device}")
model = SentenceTransformer(MODEL_NAME, device=device)
logger.info("Model loaded successfully.")


def embed_jsonl_sentences(
    input_file: str,
    output_file: str,
):
    logger.info(f"Embedding sentences from: {input_file}")
    logger.info(f"🔥 Using device: {device}")

    # Load input records
    input_path = Path(input_file)
    records = []
    texts = []
    with input_path.open("r", encoding="utf-8") as fin:
        for line in tqdm(fin, desc="Loading records", unit="record"):
            record = json.loads(line)
            text = record.get("text", "").strip()
            logger.info(
                f"Processing record: {record.get('id', 'unknown')} - Text length: {len(text)}"
            )
            if text:
                records.append(record)
                texts.append(text)

    # Embed in batches
    logger.info(f"🔍 Encoding {len(texts)} sentences...")
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    # Save output JSONL
    output_path = Path(output_file)
    with output_path.open("w", encoding="utf-8") as fout:
        for record, embedding in zip(records, embeddings):
            record["embedding"] = embedding.tolist()
            fout.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info(f"✅ Saved {len(records)} embedded records to: {output_path}")


def main():
    jsonl_files = BASE_CLEANED_JSONL_PATH.glob("*.jsonl")
    for jsonl_file in jsonl_files:
        embed_jsonl_sentences(
            input_file=jsonl_file,
            output_file=EMBEDDING_JSONL_PATH / jsonl_file.name,
        )


if __name__ == "__main__":
    main()
