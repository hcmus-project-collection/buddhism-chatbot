import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from datasets import Dataset
from dotenv import load_dotenv
from huggingface_hub import HfApi, upload_file
from loguru import logger

load_dotenv()

# Configuration
DATASET_ID = "vanloc1808/buddhist-scholar-test-set"
OUTPUT_PATH = "evaluation/test_dataset/test_set.json"
README_PATH = "evaluation/test_dataset/dataset_README.md"

# Initialize Hugging Face API
api = HfApi()

def analyze_dataset() -> dict[str, Any]:
    """Analyze the dataset to gather statistics and information."""
    logger.info("Analyzing dataset...")

    with Path(OUTPUT_PATH).open(encoding="utf-8") as f:
        data = json.load(f)

    # Basic statistics
    total_questions = len(data)

    # Analyze question and answer lengths
    question_lengths = [len(item["question"]) for item in data]
    answer_lengths = [len(item["answer"]) for item in data]

    avg_question_length = sum(question_lengths) / len(question_lengths)
    avg_answer_length = sum(answer_lengths) / len(answer_lengths)

    # Get some sample questions for different topics
    samples = data[:5] if len(data) >= 5 else data

    stats = {
        "total_questions": total_questions,
        "avg_question_length": round(avg_question_length, 2),
        "avg_answer_length": round(avg_answer_length, 2),
        "min_question_length": min(question_lengths),
        "max_question_length": max(question_lengths),
        "min_answer_length": min(answer_lengths),
        "max_answer_length": max(answer_lengths),
        "samples": samples,
    }

    logger.info(f"Dataset analysis complete: {total_questions} Q&A pairs")
    return stats

def generate_readme(stats: dict[str, Any]) -> str:
    """Generate a comprehensive README for the dataset."""
    readme_content = f"""---
license: mit
task_categories:
- question-answering
- text-generation
language:
- vi
tags:
- buddhism
- vietnamese
- qa
- religion
- chatbot-evaluation
size_categories:
- 1K<n<10K
configs:
- config_name: default
  data_files:
  - split: train
    path: "*.json"
---

# Vietnamese Buddhist Scholar Test Set

## Dataset Description

This dataset contains {stats['total_questions']} Vietnamese question-answer pairs focused on Buddhist teachings and literature. The dataset was created to evaluate chatbots' knowledge and understanding of Buddhist concepts, particularly for Vietnamese-speaking users.

## Dataset Details

### Dataset Summary

- **Language**: Vietnamese
- **Task**: Question Answering, Chatbot Evaluation
- **Domain**: Buddhism, Religious Studies
- **Size**: {stats['total_questions']} question-answer pairs
- **Format**: JSON with "question" and "answer" fields

### Dataset Structure

Each entry contains:
- `question`: A question in Vietnamese about Buddhist teachings
- `answer`: The corresponding answer extracted from Buddhist texts

### Statistics

- **Total Q&A pairs**: {stats['total_questions']}
- **Average question length**: {stats['avg_question_length']} characters
- **Average answer length**: {stats['avg_answer_length']} characters
- **Question length range**: {stats['min_question_length']} - {stats['max_question_length']} characters
- **Answer length range**: {stats['min_answer_length']} - {stats['max_answer_length']} characters

## Sample Data

```json
{json.dumps(stats['samples'][:3], ensure_ascii=False, indent=2)}
```

## Data Sources

The questions and answers were generated from Vietnamese Buddhist texts and literature, including:
- Classical Buddhist scriptures translated into Vietnamese
- Buddhist scholarly works
- Religious teachings and commentaries

## Intended Use

### Primary Use Cases

1. **Chatbot Evaluation**: Test Vietnamese chatbots' understanding of Buddhist concepts
2. **Question Answering Models**: Train or evaluate QA models on religious/cultural content
3. **Educational Tools**: Develop learning applications for Buddhist studies
4. **Cultural AI**: Improve AI systems' understanding of Vietnamese Buddhist culture

### Considerations

- The dataset focuses specifically on Buddhist teachings and may not be suitable for general knowledge evaluation
- Answers are based on traditional Buddhist texts and interpretations
- Users should be aware of the religious and cultural context when using this dataset

## Data Collection Process

The dataset was created by:
1. Processing Vietnamese Buddhist texts and literature
2. Extracting relevant passages using document processing tools
3. Generating question-answer pairs using AI models
4. Manual review and quality control
5. Formatting and validation

## Dataset Creation

**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Creator**: vanloc1808
**Processing Tools**: Azure AI Inference, Docling, Custom scripts

## Loading the Dataset

```python
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("vanloc1808/buddhist-scholar-test-set")

# Access the data
for item in dataset['train']:
    print(f"Q: {{item['question']}}")
    print(f"A: {{item['answer']}}")
    print("---")
```

## Evaluation Metrics

When using this dataset for evaluation, consider:
- **Semantic Similarity**: How well answers capture the meaning of reference answers
- **Cultural Accuracy**: Correctness within Buddhist and Vietnamese cultural context
- **Language Quality**: Fluency and naturalness of Vietnamese responses
- **Factual Correctness**: Accuracy of Buddhist teachings and concepts

## Limitations

- Limited to Vietnamese language and Buddhist domain
- May contain biases present in source materials
- Answers reflect traditional interpretations and may not cover modern perspectives
- Quality may vary across different topics within Buddhism

## Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{{buddhist_scholar_vietnamese_2024,
  title={{Vietnamese Buddhist Scholar Test Set}},
  author={{vanloc1808}},
  year={{2024}},
  url={{https://huggingface.co/datasets/vanloc1808/buddhist-scholar-test-set}}
}}
```

## License

This dataset is released under the MIT License. See LICENSE for more details.

## Contact

For questions or issues regarding this dataset, please contact the creator through Hugging Face.
"""

    return readme_content

def update_readme() -> None:
    """Update the dataset README on Hugging Face Hub."""
    logger.info("Starting README update process...")

    try:
        # Analyze the dataset
        stats = analyze_dataset()

        # Generate README content
        readme_content = generate_readme(stats)

        # Save README locally
        with Path(README_PATH).open("w", encoding="utf-8") as f:
            f.write(readme_content)

        logger.info(f"README saved locally to {README_PATH}")

        # Upload to Hugging Face Hub
        logger.info("Uploading README to Hugging Face Hub...")

        upload_file(
            path_or_fileobj=README_PATH,
            path_in_repo="README.md",
            repo_id=DATASET_ID,
            repo_type="dataset",
            commit_message=(
                "Update dataset README - "
                f"{datetime.now(tz=UTC).strftime('%Y-%m-%d %H:%M:%S')}"
            ),
        )

        logger.info("README successfully updated on Hugging Face Hub!")

        # Also update the dataset itself to ensure it's in sync
        logger.info("Updating dataset on Hub...")
        with Path(OUTPUT_PATH).open(encoding="utf-8") as f:
            data = json.load(f)

        dataset = Dataset.from_list(data)
        dataset.push_to_hub(
            DATASET_ID,
            commit_message=(
                "Update dataset - "
                f"{datetime.now(tz=UTC).strftime('%Y-%m-%d %H:%M:%S')}"
            ),
        )

        logger.info("Dataset update complete!")

    except Exception as e:
        logger.error(f"Error updating README: {e}")
        raise

if __name__ == "__main__":
    update_readme()
