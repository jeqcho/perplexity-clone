"""Analyzer to determine optimal number of search results based on query complexity."""

from src.llm.openai_client import OpenAIClient
from src.config import Config


class ResultAnalyzer:
    """Analyzes queries to determine optimal number of search results to fetch."""

    def __init__(self, llm_client: OpenAIClient = None):
        """Initialize the result analyzer.

        Args:
            llm_client: OpenAI client instance. If not provided, creates a new one.
        """
        self.llm_client = llm_client or OpenAIClient()

    def determine_result_count(self, query: str) -> int:
        """Determine optimal number of search results for the given query.

        Args:
            query: The user's search query

        Returns:
            Number of search results to fetch (between MIN and MAX_SEARCH_RESULTS)

        Raises:
            Exception: If LLM API call fails
        """
        prompt = f"""Analyze the following search query and determine how many search results (between {Config.MIN_SEARCH_RESULTS} and {Config.MAX_SEARCH_RESULTS}) would be optimal to answer it comprehensively.

Query: "{query}"

Consider:
- Simple factual queries (e.g., "What is the capital of France?") need fewer results (5-6)
- Complex analytical queries (e.g., "Compare the economic impacts of AI on developing vs developed nations") need more results (8-10)
- Queries requiring multiple perspectives or recent information need more results

Respond with ONLY a single number between {Config.MIN_SEARCH_RESULTS} and {Config.MAX_SEARCH_RESULTS}."""

        try:
            response = self.llm_client.generate(prompt, max_tokens=20, temperature=0)

            # Handle empty or invalid response
            if not response or not response.strip():
                # Default to middle value if LLM fails
                return (Config.MIN_SEARCH_RESULTS + Config.MAX_SEARCH_RESULTS) // 2

            # Extract number from response (handle cases like "8 results" or "I recommend 7")
            import re
            numbers = re.findall(r'\d+', response.strip())

            if not numbers:
                # Default to middle value
                return (Config.MIN_SEARCH_RESULTS + Config.MAX_SEARCH_RESULTS) // 2

            result_count = int(numbers[0])

            # Clamp to valid range
            result_count = max(Config.MIN_SEARCH_RESULTS, min(Config.MAX_SEARCH_RESULTS, result_count))

            return result_count

        except (ValueError, Exception) as e:
            # Fail fast on errors as per requirements
            raise Exception(f"Failed to determine result count: {str(e)}") from e
