import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

logger.add("evaluation/evaluate_answer/find_average.log")


def extract_metrics(
    json_file: str,
) -> tuple[
    list[float],
    list[float],
    list[int],
    list[float],
    list[float],
    list[int],
]:
    """Extract metrics from a JSON file."""
    with Path(json_file).open(encoding="utf-8") as f:
        data = json.loads(f.read())
    logger.info(f"Total items: {len(data)}")

    cosine_similarities_without_tools = [
        item["cosine_similarity"]
        for item in data
        if "cosine_similarity" in item and item["using_tools"]
    ]
    cosine_similarities_with_tools = [
        item["cosine_similarity"]
        for item in data
        if "cosine_similarity" in item and not item["using_tools"]
    ]
    bert_scores_without_tools = [
        item["bert_score"]
        for item in data
        if "bert_score" in item
    ]
    bert_scores_with_tools = [
        item["bert_score"]
        for item in data
        if "bert_score" in item and not item["using_tools"]
    ]
    gpt_similarity_scores_without_tools = [
        item["gpt_similarity_score"]
        for item in data
        if "gpt_similarity_score" in item
    ]
    gpt_similarity_scores_with_tools = [
        item["gpt_similarity_score"]
        for item in data
        if "gpt_similarity_score" in item and not item["using_tools"]
    ]
    return (
        cosine_similarities_without_tools,
        bert_scores_without_tools,
        gpt_similarity_scores_without_tools,
        cosine_similarities_with_tools,
        bert_scores_with_tools,
        gpt_similarity_scores_with_tools,
    )


def find_average(
    cosine_similarities: list[float],
    bert_scores: list[float],
    gpt_similarity_scores: list[int],
) -> tuple[float, float, float]:
    """Find the average of the metrics."""
    return (
        np.mean(cosine_similarities),
        np.mean(bert_scores),
        np.mean(gpt_similarity_scores),
    )


def main() -> None:
    """Find the average of the metrics."""
    (
        cosine_similarities_without_tools,
        bert_scores_without_tools,
        gpt_similarity_scores_without_tools,
        cosine_similarities_with_tools,
        bert_scores_with_tools,
        gpt_similarity_scores_with_tools,
    ) = extract_metrics(
        "evaluation/similarity/all_similarities_20250725_085945.json",
    )

    # Histograms: without tools
    plt.figure(figsize=(10, 5))
    plt.hist(
        cosine_similarities_without_tools,
        bins=20,
        alpha=0.5,
        label="Cosine Similarity Without Tools",
    )
    plt.legend()
    plt.savefig(
        "evaluation/similarity/cosine_similarity_histogram_without_tools.png",
    )
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.hist(
        bert_scores_without_tools,
        bins=20,
        alpha=0.5,
        label="BERT Score Without Tools",
    )
    plt.legend()
    plt.savefig(
        "evaluation/similarity/bert_score_histogram_without_tools.png",
    )
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.hist(
        gpt_similarity_scores_without_tools,
        bins=20,
        alpha=0.5,
        label="GPT Similarity Score Without Tools",
    )
    plt.legend()
    plt.savefig(
        (
            "evaluation/similarity/gpt_similarity_score_histogram_"
            "without_tools.png"
        ),
    )
    plt.close()

    # Histograms: with tools
    plt.figure(figsize=(10, 5))
    plt.hist(
        cosine_similarities_with_tools,
        bins=20,
        alpha=0.5,
        label="Cosine Similarity With Tools",
    )
    plt.legend()
    plt.savefig(
        "evaluation/similarity/cosine_similarity_histogram_with_tools.png",
    )
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.hist(
        bert_scores_with_tools,
        bins=20,
        alpha=0.5,
        label="BERT Score With Tools",
    )
    plt.legend()
    plt.savefig("evaluation/similarity/bert_score_histogram_with_tools.png",
    )
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.hist(
        gpt_similarity_scores_with_tools,
        bins=20,
        alpha=0.5,
        label="GPT Similarity Score With Tools",
    )
    plt.legend()
    plt.savefig(
        "evaluation/similarity/gpt_similarity_score_histogram_with_tools.png",
    )
    plt.close()

    # Averages: without tools
    (
        avg_cosine_similarity_without_tools,
        avg_bert_score_without_tools,
        avg_gpt_similarity_score_without_tools,
    ) = find_average(
        cosine_similarities_without_tools,
        bert_scores_without_tools,
        gpt_similarity_scores_without_tools,
    )
    logger.info(
        "Average Cosine Similarity without tools: "
        f"{avg_cosine_similarity_without_tools}",
    )
    logger.info(
        f"Average BERT Score without tools: {avg_bert_score_without_tools}",
    )
    logger.info(
        "Average GPT Similarity Score without tools: "
        f"{avg_gpt_similarity_score_without_tools}",
    )

    # Averages: with tools
    (
        avg_cosine_similarity_with_tools,
        avg_bert_score_with_tools,
        avg_gpt_similarity_score_with_tools,
    ) = find_average(
        cosine_similarities_with_tools,
        bert_scores_with_tools,
        gpt_similarity_scores_with_tools,
    )
    logger.info(
        "Average Cosine Similarity with tools: "
        f"{avg_cosine_similarity_with_tools}",
    )
    logger.info(
        f"Average BERT Score with tools: {avg_bert_score_with_tools}",
    )
    logger.info(
        "Average GPT Similarity Score with tools: "
        f"{avg_gpt_similarity_score_with_tools}",
    )

    # Combine and analyze all
    cosine_similarities =(
        cosine_similarities_with_tools
        + cosine_similarities_without_tools
    )
    bert_scores = bert_scores_with_tools + bert_scores_without_tools
    gpt_similarity_scores = (
        gpt_similarity_scores_with_tools + gpt_similarity_scores_without_tools
    )

    avg_cosine_similarity, avg_bert_score, avg_gpt_similarity_score = (
        find_average(
            cosine_similarities,
            bert_scores,
            gpt_similarity_scores,
        )
    )

    plt.figure(figsize=(10, 5))
    plt.hist(
        cosine_similarities,
        bins=20,
        alpha=0.5,
        label="Cosine Similarity",
    )
    plt.legend()
    plt.savefig(
        "evaluation/similarity/cosine_similarity_histogram_combined.png",
    )
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.hist(bert_scores, bins=20, alpha=0.5, label="BERT Score")
    plt.legend()
    plt.savefig("evaluation/similarity/bert_score_histogram_combined.png")
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.hist(
        gpt_similarity_scores,
        bins=20,
        alpha=0.5,
        label="GPT Similarity Score",
    )
    plt.legend()
    plt.savefig(
        "evaluation/similarity/gpt_similarity_score_histogram_combined.png",
    )
    plt.close()

    logger.info(f"Average Cosine Similarity: {avg_cosine_similarity}")
    logger.info(f"Average BERT Score: {avg_bert_score}")
    logger.info(f"Average GPT Similarity Score: {avg_gpt_similarity_score}")


if __name__ == "__main__":
    main()
