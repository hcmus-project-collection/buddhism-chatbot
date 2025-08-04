import json
import os
import uuid
from pathlib import Path

import torch
from dotenv import load_dotenv
from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from loguru import logger
from sentence_transformers import SentenceTransformer

load_dotenv()

device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)

BASE_MD_PATH = Path("docling/pdfs")
RAW_JSONL_PATH = Path("jsonl/raw")
EMBEDDING_JSONL_PATH = Path("jsonl/embeddings")
EMBEDDING_JSONL_PATH.mkdir(parents=True, exist_ok=True)

MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-base")
BATCH_SIZE = 16
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 128

logger.info(f"Loading model: {MODEL_NAME} on device: {device}")
model = SentenceTransformer(MODEL_NAME, device=device)
logger.info("Model loaded successfully.")


def load_metadata_from_jsonl(jsonl_path: Path) -> dict:
    """Load metadata from the first line of a JSONL file."""
    if not jsonl_path.exists():
        return {}
    with jsonl_path.open("r", encoding="utf-8") as f:
        try:
            line = f.readline()
            data = json.loads(line)
            return data.get("meta", {})
        except (json.JSONDecodeError, IndexError):
            return {}


def embed_markdown_chunks(
    input_dir: str,
    output_file: str,
) -> None:
    """Load markdown files, chunks them, and creates embeddings."""
    logger.info(f"Loading markdown files from: {input_dir}")
    loader = DirectoryLoader(input_dir, glob="**/*.md", show_progress=True)
    docs = loader.load()

    # Load metadata and add it to documents
    for doc in docs:
        source_path = Path(doc.metadata["source"])
        jsonl_filename = f"{source_path.stem}_with_ner.jsonl"
        jsonl_path = RAW_JSONL_PATH / jsonl_filename
        extra_meta = load_metadata_from_jsonl(jsonl_path)
        doc.metadata.update(extra_meta)

    logger.info(f"Splitting {len(docs)} documents into chunks...")
    splitter = MarkdownTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    logger.info(f"Created {len(chunks)} chunks.")

    texts = [chunk.page_content for chunk in chunks]

    # Embed in batches
    logger.info(f"🔍 Encoding {len(texts)} chunks...")
    logger.info(f"🔥 Using device: {device}")
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    # Save output JSONL
    output_path = Path(output_file)
    with output_path.open("w", encoding="utf-8") as fout:
        for chunk, embedding in zip(chunks, embeddings, strict=False):
            record = {
                "id": str(uuid.uuid4()),
                "text": chunk.page_content,
                "metadata": chunk.metadata,
                "embedding": embedding.tolist(),
            }
            fout.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info(f"✅ Saved {len(chunks)} embedded chunks to: {output_path}")


def main() -> None:
    """Implement the embedding pipeline."""
    embed_markdown_chunks(
        input_dir=str(BASE_MD_PATH),
        output_file=str(EMBEDDING_JSONL_PATH / "embedded_chunks.jsonl"),
    )


if __name__ == "__main__":
    main()
