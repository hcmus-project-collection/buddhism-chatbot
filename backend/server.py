import logging

from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL_NAME, DEVICE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=DEVICE)
