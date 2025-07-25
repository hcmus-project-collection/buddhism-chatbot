import json
from datetime import datetime

import json_repair
from loguru import logger
from bert_score import score

logger.add(f"evaluate_answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")


def calculate_bert_score(expected_answer: str, actual_answer: str) -> float:
    """Calculate the BERT score between the expected and actual answers."""
    logger.info(f"Calculating BERT score between {expected_answer} and {actual_answer}")
    # BERT score expects lists of candidates and references
    bert_score = score([actual_answer], [expected_answer], lang="vi")
    # Extract F1 score (third element) from the tuple
    f1_score = bert_score[2].item()  # Convert tensor to float
    logger.info(f"BERT score: {f1_score}")
    return f1_score


def evaluate_json_file(json_file: str) -> list[dict]:
    """Evaluate answer from a JSON file."""
    with open(json_file, "r") as f:
        data = json_repair.loads(f.read())

    for item in data:
        item["bert_score"] = calculate_bert_score(
            item["expected_answer"],
            item["actual_answer"],
        )
        # Convert numpy float32 to Python float for JSON serialization
        item["bert_score"] = float(item["bert_score"])
    return data


if __name__ == "__main__":
    data = evaluate_json_file(
        "evaluation/results/evaluation_results_20250724_112717.json",
    )
    with open(
        f"evaluation/similarity/bert_score_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        "w",
    ) as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
