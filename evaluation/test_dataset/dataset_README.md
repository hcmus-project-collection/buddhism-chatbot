---
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

This dataset contains 1008 Vietnamese question-answer pairs focused on Buddhist teachings and literature. The dataset was created to evaluate chatbots' knowledge and understanding of Buddhist concepts, particularly for Vietnamese-speaking users.

## Dataset Details

### Dataset Summary

- **Language**: Vietnamese
- **Task**: Question Answering, Chatbot Evaluation
- **Domain**: Buddhism, Religious Studies
- **Size**: 1008 question-answer pairs
- **Format**: JSON with "question" and "answer" fields

### Dataset Structure

Each entry contains:
- `question`: A question in Vietnamese about Buddhist teachings
- `answer`: The corresponding answer extracted from Buddhist texts

### Statistics

- **Total Q&A pairs**: 1008
- **Average question length**: 54.23 characters
- **Average answer length**: 75.18 characters
- **Question length range**: 15 - 121 characters
- **Answer length range**: 2 - 417 characters

## Sample Data

```json
[
  {
    "question": "Quyển Ba của tác phẩm có tên là gì?",
    "answer": "Quyển Ba: Bàn rộng để khơi mở và củng cố niềm tin"
  },
  {
    "question": "Bài văn khuyên tu hành nằm ở trang bao nhiêu?",
    "answer": "139"
  },
  {
    "question": "Theo đoạn văn, điều gì được cho là nặng nề hơn cả tham dục?",
    "answer": "Chướng ngại của lý còn nặng nề hơn cả tham dục"
  }
]
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

**Created**: 2025-07-23
**Creator**: vanloc1808
**Processing Tools**: Azure AI Inference, Docling, Custom scripts

## Loading the Dataset

```python
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("vanloc1808/buddhist-scholar-test-set")

# Access the data
for item in dataset['train']:
    print(f"Q: {item['question']}")
    print(f"A: {item['answer']}")
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
@dataset{buddhist_scholar_vietnamese_2024,
  title={Vietnamese Buddhist Scholar Test Set},
  author={vanloc1808},
  year={2024},
  url={https://huggingface.co/datasets/vanloc1808/buddhist-scholar-test-set}
}
```

## License

This dataset is released under the MIT License. See LICENSE for more details.

## Contact

For questions or issues regarding this dataset, please contact the creator through Hugging Face.
