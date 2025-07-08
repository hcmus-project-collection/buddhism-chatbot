import os

from dotenv import load_dotenv

from qdrant_client import QdrantClient

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    api_key=os.getenv("QDRANT_API_KEY", "your_secret_api_key_here"),
)
print(client.get_collections())
