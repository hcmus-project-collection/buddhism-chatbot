# Evaluation

This directory contains scripts and tools for evaluating the performance of the SanghaGPT backend using the test dataset from HuggingFace.

## Overview

The evaluation system tests the backend's performance using the `vanloc1808/buddhist-scholar-test-set` dataset from HuggingFace. It measures response times, accuracy, and other performance metrics for both regular and tool-enabled query modes.

## Features

- **Dataset Integration**: Automatically loads test datasets from HuggingFace
- **Dual Mode Testing**: Tests both regular and tool-enabled backend endpoints
- **Performance Metrics**: Measures response time, success rate, and other key metrics
- **Comprehensive Reporting**: Generates detailed reports in JSON, CSV, and console formats
- **Error Handling**: Robust error handling and timeout management
- **Configurable**: Command-line interface with multiple configuration options

## Installation

1. Install the evaluation dependencies:
```bash
pip install -r evaluation/requirements.txt
```

2. Ensure your backend is running (default: http://localhost:8000)

## Usage

### Basic Usage

Run the evaluation with default settings:
```bash
python evaluation/evaluate_backend.py
```

### Advanced Usage

```bash
# Test with custom backend URL
python evaluation/evaluate_backend.py --backend-url http://localhost:8080

# Limit the number of queries for quick testing
python evaluation/evaluate_backend.py --max-queries 10

# Skip tool-enabled mode testing
python evaluation/evaluate_backend.py --no-tools

# Use a different dataset
python evaluation/evaluate_backend.py --dataset your-username/your-test-dataset

# Custom output directory
python evaluation/evaluate_backend.py --output-dir ./my-results
```

### Command Line Options

- `--backend-url`: Backend URL (default: http://localhost:8000)
- `--dataset`: HuggingFace dataset name (default: vanloc1808/buddhist-scholar-test-set)
- `--max-queries`: Maximum number of queries to test (default: all)
- `--no-tools`: Skip tool-enabled mode testing
- `--output-dir`: Output directory for results (default: evaluation/results)

## Output Files

The evaluation generates several output files:

### 1. Detailed Results (`evaluation_results_YYYYMMDD_HHMMSS.json`)
Contains detailed information for each query:
```json
{
  "query": "What is the meaning of enlightenment in Buddhism?",
  "expected_answer": "Expected answer from dataset",
  "actual_answer": "Backend response",
  "response_time": 1.234,
  "status_code": 200,
  "using_tools": false,
  "relevant_texts_count": 5,
  "timestamp": "2024-01-15T10:30:45"
}
```

### 2. Metrics Summary (`evaluation_metrics_YYYYMMDD_HHMMSS.json`)
Contains aggregated performance metrics:
```json
{
  "total_queries": 100,
  "successful_queries": 95,
  "failed_queries": 5,
  "avg_response_time": 1.234,
  "min_response_time": 0.456,
  "max_response_time": 3.789,
  "p95_response_time": 2.567,
  "success_rate": 95.0,
  "tool_enabled_queries": 50,
  "regular_queries": 50
}
```

### 3. CSV Export (`evaluation_results_YYYYMMDD_HHMMSS.csv`)
Tabular format for easy analysis in spreadsheet applications or data analysis tools.

### 4. Evaluation Log (`evaluation_YYYY-MM-DD_HH-MM-SS.log`)
Detailed log of the evaluation process including errors and warnings.

## Performance Metrics

The evaluation measures the following key metrics:

### Response Time Metrics
- **Average Response Time**: Mean response time across all queries
- **Minimum Response Time**: Fastest response time
- **Maximum Response Time**: Slowest response time
- **95th Percentile**: 95% of responses are faster than this time

### Success Metrics
- **Success Rate**: Percentage of queries that returned successful responses (HTTP 200)
- **Failed Queries**: Number of queries that failed (timeouts, errors, etc.)

### Mode Comparison
- **Regular Mode**: Queries processed without tools
- **Tool-Enabled Mode**: Queries processed with tools enabled

## Dataset Structure

The evaluation script expects the HuggingFace dataset to have the following structure:

### Required Fields
- `question` or `query` or `input`: The query text to send to the backend
- `answer` or `expected_answer` (optional): Expected answer for comparison

### Example Dataset Format
```json
{
  "question": "What is meditation in Buddhism?",
  "answer": "Meditation in Buddhism is a practice of mental cultivation..."
}
```

## Troubleshooting

### Common Issues

1. **Backend Not Running**
   ```
   Error: Backend health check failed
   ```
   Solution: Ensure your backend is running on the specified URL

2. **Dataset Not Found**
   ```
   Error: Failed to load dataset
   ```
   Solution: Check the dataset name and ensure you have internet connectivity

3. **Timeout Errors**
   ```
   Error: Query timed out
   ```
   Solution: The backend may be overloaded or the query is complex. Consider increasing timeout or reducing query complexity.

4. **Missing Dependencies**
   ```
   ModuleNotFoundError: No module named 'datasets'
   ```
   Solution: Install the required dependencies with `pip install -r evaluation/requirements.txt`

### Performance Tips

1. **Quick Testing**: Use `--max-queries 10` for rapid testing during development
2. **Single Mode**: Use `--no-tools` to test only regular mode and reduce evaluation time
3. **Parallel Testing**: The script runs queries sequentially. For high-volume testing, consider running multiple instances with different dataset subsets

## Integration with CI/CD

You can integrate the evaluation into your CI/CD pipeline:

```bash
# Run evaluation and check if success rate is above threshold
python evaluation/evaluate_backend.py --max-queries 20 > eval_output.txt
if grep -q "Success Rate: 9[0-9]" eval_output.txt; then
    echo "Evaluation passed (≥90% success rate)"
    exit 0
else
    echo "Evaluation failed (<90% success rate)"
    exit 1
fi
```

## Contributing

To add new evaluation features:

1. Extend the `BackendEvaluator` class with new methods
2. Add corresponding metrics to the `EvaluationMetrics` dataclass
3. Update the output generation methods
4. Add tests to verify the new functionality

## Example Results

```
============================================================
EVALUATION SUMMARY
============================================================
Total Queries: 100
Successful: 95
Failed: 5
Success Rate: 95.0%
Regular Mode Queries: 50
Tool Mode Queries: 50

Response Time Statistics:
  Average: 1.234s
  Minimum: 0.456s
  Maximum: 3.789s
  95th Percentile: 2.567s

Sample Results:

--- Sample 1 ---
Query: What is the meaning of enlightenment in Buddhism...
Answer: Enlightenment in Buddhism refers to the state of awakening...
Response Time: 1.123s
Tools Used: False
Status: ✓
```