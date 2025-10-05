"""Base agent class defining the interface for all search result processing agents."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.llm.openai_client import OpenAIClient


class BaseAgent(ABC):
    """Abstract base class for all agents that process search results."""

    def __init__(self, llm_client: OpenAIClient = None):
        """Initialize the agent.

        Args:
            llm_client: OpenAI client instance. If not provided, creates a new one.
        """
        self.llm_client = llm_client or OpenAIClient()

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return the name of this agent's strategy.

        Returns:
            A string describing the agent's strategy
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt that defines this agent's behavior.

        Returns:
            System prompt string for the LLM
        """
        pass

    def process_query(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        """Process a query using search results and return an answer with citations.

        Args:
            query: The user's search query
            search_results: List of search results from SerpAPI

        Returns:
            Answer with numbered citations in format [1], [2], etc.

        Raises:
            Exception: If LLM API call fails
        """
        # Format search results for the prompt
        results_text = self._format_search_results(search_results)

        # Build the user prompt
        user_prompt = f"""Query: {query}

Search Results:
{results_text}

Provide a comprehensive answer to the query using the search results above. You MUST cite sources using numbered citations in the format [1], [2], etc., where the number corresponds to the search result index.

Your answer should:
1. Directly address the user's query
2. Use information from the search results
3. Include numbered citations [N] immediately after facts, quotes, or claims
4. Be well-structured and coherent
5. Provide the citation list at the end in the format:

Citations:
[1] Title - URL
[2] Title - URL
..."""

        try:
            response = self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=self.get_system_prompt(),
                max_tokens=2000,
                temperature=0.7
            )
            return response

        except Exception as e:
            raise Exception(f"{self.get_strategy_name()} agent failed: {str(e)}") from e

    def _format_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results for inclusion in the prompt.

        Args:
            search_results: List of search result dictionaries

        Returns:
            Formatted string of search results
        """
        formatted = []
        for result in search_results:
            formatted.append(
                f"[{result['index']}] {result['title']}\n"
                f"URL: {result['link']}\n"
                f"Snippet: {result['snippet']}\n"
            )
        return "\n".join(formatted)
