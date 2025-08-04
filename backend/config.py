import os

import torch
from dotenv import load_dotenv

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

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "buddhism_religion")

# Embedding model configuration
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "intfloat/multilingual-e5-base",
)

DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)
PORT = int(os.getenv("PORT", 8000))
