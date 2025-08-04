import json
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from datasets import load_dataset
from loguru import logger

logger.add(f"evaluation/evaluation_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")


@dataclass
class EvaluationResult:
    """Data class to store evaluation results for a single query."""

    query: str
    expected_answer: str | None
    actual_answer: str
    response_time: float
    status_code: int
    using_tools: bool
    relevant_texts_count: int
    timestamp: str

@dataclass
class EvaluationMetrics:
    """Data class to store aggregated evaluation metrics."""

    total_queries: int
    successful_queries: int
    failed_queries: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    success_rate: float
    tool_enabled_queries: int
    regular_queries: int

class BackendEvaluator:
    """Main class for evaluating backend performance."""

    def __init__(self, backend_url: str = "https://backend-buddhismchatbot.nguyenvanloc.com") -> None:
        self.backend_url = backend_url
        self.results: list[EvaluationResult] = []
        self.dataset = None

    def load_test_dataset(self, dataset_name: str = "vanloc1808/buddhist-scholar-test-set") -> bool:
        """Load the test dataset from HuggingFace."""
        try:
            logger.info(f"Loading dataset: {dataset_name}")
            self.dataset = load_dataset(dataset_name)
            logger.info(f"Dataset loaded successfully. Available splits: {list(self.dataset.keys())}")
            return True
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            return False

    def check_backend_health(self) -> bool:
        """Check if the backend is running and healthy."""
        try:
            # Test with a simple query to check if the backend is responsive
            test_payload = {
                "query": "test",
                "top_k": 1,
                "metadata_filter": {},
                "using_tools": False,
            }

            headers = {
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "origin": "https://buddhism-chatbot.nguyenvanloc.com",
                "referer": "https://buddhism-chatbot.nguyenvanloc.com/",
                "user-agent": "Mozilla/5.0 (compatible; EvaluationBot/1.0)",
            }

            response = requests.post(
                f"{self.backend_url}/query",
                json=test_payload,
                headers=headers,
                timeout=30,
            )

            if response.status_code == 200:
                logger.info("Backend is healthy and running")
                return True
            else:
                logger.error(f"Backend health check failed with status: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Backend health check failed: {e}")
            return False

    def query_backend(self, query: str, using_tools: bool = False, top_k: int = 5) -> tuple[dict, float]:
        """Send a query to the backend and measure response time."""
        start_time = time.time()

        payload = {
            "query": query,
            "top_k": top_k,
            "metadata_filter": {},
            "using_tools": using_tools,
        }

        # Headers matching the production frontend requests
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5,fr-FR;q=0.4,fr;q=0.3",
            "content-type": "application/json",
            "origin": "https://buddhism-chatbot.nguyenvanloc.com",
            "referer": "https://buddhism-chatbot.nguyenvanloc.com/",
            "user-agent": "Mozilla/5.0 (compatible; EvaluationBot/1.0)",
        }

        try:
            response = requests.post(
                f"{self.backend_url}/query",
                json=payload,
                headers=headers,
                timeout=30,
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                return response.json(), response_time
            else:
                logger.warning(f"Query failed with status {response.status_code}: {response.text}")
                return {"error": f"HTTP {response.status_code}"}, response_time

        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            logger.error(f"Query timed out after {response_time:.2f}s")
            return {"error": "timeout"}, response_time
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Query failed: {e}")
            return {"error": str(e)}, response_time

    def evaluate_single_query(
        self,
        query: str,
        expected_answer: str | None = None,
        using_tools: bool = False,
    ) -> EvaluationResult | None:
        """Evaluate a single query."""
        logger.debug(f"Evaluating query: {query[:100]}...")

        response_data, response_time = self.query_backend(query, using_tools)

        if "error" in response_data:
            actual_answer = f"ERROR: {response_data['error']}"
            status_code = 500
            relevant_texts_count = 0
        else:
            actual_answer = response_data.get("answer", "No answer provided")
            status_code = 200
            relevant_texts_count = len(response_data.get("relevant_texts", []))

        result = EvaluationResult(
            query=query,
            expected_answer=expected_answer,
            actual_answer=actual_answer,
            response_time=response_time,
            status_code=status_code,
            using_tools=using_tools,
            relevant_texts_count=relevant_texts_count,
            timestamp=datetime.now().isoformat(),
        )

        self.results.append(result)
        return result

    def run_evaluation(self, max_queries: int | None = None, test_both_modes: bool = True) -> EvaluationMetrics | None:
        """Run the complete evaluation process."""
        if self.dataset is None:
            logger.error("No dataset loaded. Please load a dataset first.")
            return None

        if not self.check_backend_health():
            logger.error("Backend is not healthy. Aborting evaluation.")
            return None

        # Choose the test split, or fall back to available splits
        available_splits = list(self.dataset.keys())
        test_split = "test" if "test" in available_splits else available_splits[0]
        test_data = self.dataset[test_split]

        logger.info(f"Using split '{test_split}' with {len(test_data)} samples")

        # Limit the number of queries if specified
        if max_queries:
            test_data = test_data.select(range(min(max_queries, len(test_data))))
            logger.info(f"Limited evaluation to {len(test_data)} queries")

        # Run evaluation
        total_queries = len(test_data) * (2 if test_both_modes else 1)
        logger.info(f"Starting evaluation with {total_queries} total queries")

        for i, sample in enumerate(test_data):
            # Extract query and expected answer from the dataset
            # Adjust these field names based on your dataset structure
            query = sample.get("question", sample.get("query", sample.get("input", "")))
            expected_answer = sample.get("answer", sample.get("expected_answer", None))

            if not query:
                logger.warning(f"Skipping sample {i}: no query found")
                continue

            # Test regular mode
            logger.info(f"Progress: {i+1}/{len(test_data)} - Testing regular mode")
            self.evaluate_single_query(query, expected_answer, using_tools=False)

            # Test tool-enabled mode if requested
            if test_both_modes:
                logger.info(f"Progress: {i+1}/{len(test_data)} - Testing tool mode")
                self.evaluate_single_query(query, expected_answer, using_tools=True)

        # Calculate metrics
        metrics = self.calculate_metrics()
        logger.info("Evaluation completed successfully")

        return metrics

    def calculate_metrics(self) -> EvaluationMetrics | None:
        """Calculate evaluation metrics from results."""
        if not self.results:
            logger.warning("No results to calculate metrics from")
            return None

        successful_results = [r for r in self.results if r.status_code == 200]
        failed_results = [r for r in self.results if r.status_code != 200]

        response_times = [r.response_time for r in self.results]
        tool_enabled_count = len([r for r in self.results if r.using_tools])
        regular_count = len([r for r in self.results if not r.using_tools])

        metrics = EvaluationMetrics(
            total_queries=len(self.results),
            successful_queries=len(successful_results),
            failed_queries=len(failed_results),
            avg_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            p95_response_time=(
                statistics.quantiles(response_times, n=20)[18]
                if len(response_times) > 1
                else response_times[0]
            ),
            success_rate=len(successful_results) / len(self.results) * 100,
            tool_enabled_queries=tool_enabled_count,
            regular_queries=regular_count,
        )

        return metrics

    def save_results(self, output_dir: str = "evaluation/results") -> tuple[Path, Path | None]:
        """Save evaluation results to files."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results as JSON
        results_file = Path(output_dir) / f"evaluation_results_{timestamp}.json"
        with Path(results_file).open("w", encoding="utf-8") as f:
            json.dump([asdict(result) for result in self.results], f, indent=2, ensure_ascii=False)

        # Save metrics
        metrics = self.calculate_metrics()
        if metrics:
            metrics_file = Path(output_dir) / f"evaluation_metrics_{timestamp}.json"
            with Path(metrics_file).open("w", encoding="utf-8") as f:
                json.dump(asdict(metrics), f, indent=2)

        # Save as CSV for easy analysis
        if self.results:
            df = pd.DataFrame([asdict(result) for result in self.results])
            csv_file = Path(output_dir) / f"evaluation_results_{timestamp}.csv"
            df.to_csv(csv_file, index=False)

        logger.info(f"Results saved to {output_dir}")
        return results_file, metrics_file if metrics else None

    def print_summary(self) -> None:
        """Print a summary of the evaluation results."""
        if not self.results:
            logger.warning("No results to summarize")
            return

        metrics = self.calculate_metrics()

        logger.info("\n" + "="*60)
        logger.info("EVALUATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Queries: {metrics.total_queries}")
        logger.info(f"Successful: {metrics.successful_queries}")
        logger.info(f"Failed: {metrics.failed_queries}")
        logger.info(f"Success Rate: {metrics.success_rate:.1f}%")
        logger.info(f"Regular Mode Queries: {metrics.regular_queries}")
        logger.info(f"Tool Mode Queries: {metrics.tool_enabled_queries}")
        logger.info("\nResponse Time Statistics:")
        logger.info(f"  Average: {metrics.avg_response_time:.3f}s")
        logger.info(f"  Minimum: {metrics.min_response_time:.3f}s")
        logger.info(f"  Maximum: {metrics.max_response_time:.3f}s")
        logger.info(f"  95th Percentile: {metrics.p95_response_time:.3f}s")

        # Show some example responses
        logger.info("\nSample Results:")
        for i, result in enumerate(self.results[:3]):
            logger.info(f"\n--- Sample {i+1} ---")
            logger.info(f"Query: {result.query[:100]}...")
            logger.info(f"Answer: {result.actual_answer[:200]}...")
            logger.info(f"Response Time: {result.response_time:.3f}s")
            logger.info(f"Tools Used: {result.using_tools}")
            logger.info(f"Status: {'✓' if result.status_code == 200 else '✗'}")


def main() -> None:
    """Implement the main function to run the evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate Eastern Religion Chatbot Backend")
    parser.add_argument("--backend-url", default="https://backend-buddhismchatbot.nguyenvanloc.com",
                       help="Backend URL (default: https://backend-buddhismchatbot.nguyenvanloc.com)")
    parser.add_argument("--dataset", default="vanloc1808/buddhist-scholar-test-set",
                       help="HuggingFace dataset name")
    parser.add_argument("--max-queries", type=int, default=None,
                       help="Maximum number of queries to test")
    parser.add_argument("--no-tools", action="store_true",
                       help="Skip tool-enabled mode testing")
    parser.add_argument("--output-dir", default="evaluation/results",
                       help="Output directory for results")

    args = parser.parse_args()

    # Initialize evaluator
    evaluator = BackendEvaluator(args.backend_url)

    # Load dataset
    if not evaluator.load_test_dataset(args.dataset):
        logger.error("Failed to load dataset. Exiting.")
        return 1

    # Run evaluation
    test_both_modes = not args.no_tools
    metrics = evaluator.run_evaluation(args.max_queries, test_both_modes)

    if metrics is None:
        logger.error("Evaluation failed. Exiting.")
        return 1

    # Save and display results
    evaluator.save_results(args.output_dir)
    evaluator.print_summary()

    return 0

if __name__ == "__main__":
    exit(main())
