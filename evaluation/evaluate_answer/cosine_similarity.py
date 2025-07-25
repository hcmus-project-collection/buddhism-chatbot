from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger
from datetime import datetime
import json_repair
import json


model = SentenceTransformer("intfloat/e5-base")

logger.add(f"evaluate_answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")


def calculate_similarity(expected_answer: str, actual_answer: str) -> float:
    """Calculate the similarity between the expected and actual answers."""
    logger.info(f"Calculating similarity between {expected_answer} and {actual_answer}")
    expected_embedding = model.encode(expected_answer, normalize_embeddings=True)
    actual_embedding = model.encode(actual_answer, normalize_embeddings=True)

    # Reshape embeddings to 2D arrays for cosine_similarity
    expected_embedding = expected_embedding.reshape(1, -1)
    actual_embedding = actual_embedding.reshape(1, -1)

    similarity = cosine_similarity(expected_embedding, actual_embedding)
    logger.info(f"Similarity: {similarity}")
    return similarity[0][0]  # Extract the scalar value from the 2D array

def evaluate_json_file(json_file: str) -> list[dict]:
    """Evaluate answer from a JSON file."""
    with open(json_file, "r") as f:
        data = json_repair.loads(f.read())

    for item in data:
        item["similarity"] = calculate_similarity(
            item["expected_answer"],
            item["actual_answer"],
        )
        # Convert numpy float32 to Python float for JSON serialization
        item["similarity"] = float(item["similarity"])
    return data


if __name__ == "__main__":
    data = evaluate_json_file(
        "evaluation/results/evaluation_results_20250724_112717.json",
    )
    with open(
        f"evaluation/similarity/cosine_similarity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        "w",
    ) as f:
        json.dump(data, f, indent=4, ensure_ascii=False)