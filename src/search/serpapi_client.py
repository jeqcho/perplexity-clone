"""SerpAPI client for performing Google searches."""

import requests
from typing import List, Dict, Any
from src.config import Config


class SerpAPIClient:
    """Client for interacting with SerpAPI to fetch Google search results."""

    BASE_URL = "https://serpapi.com/search"

    def __init__(self, api_key: str = None):
        """Initialize SerpAPI client.

        Args:
            api_key: SerpAPI key. If not provided, uses Config.SERPAPI_KEY
        """
        self.api_key = api_key or Config.SERPAPI_KEY
        if not self.api_key:
            raise ValueError("SerpAPI key is required")

    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Perform a Google search and return organic results.

        Args:
            query: The search query
            num_results: Number of results to fetch (default: 10)

        Returns:
            List of search result dictionaries containing title, link, snippet, etc.

        Raises:
            requests.RequestException: If the API request fails
        """
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": num_results,
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Extract organic results from SerpAPI response
            organic_results = data.get("organic_results", [])

            # Format results for agent consumption
            formatted_results = []
            for idx, result in enumerate(organic_results, 1):
                formatted_results.append({
                    "index": idx,
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", idx),
                })

            return formatted_results

        except requests.RequestException as e:
            # Fail fast on API errors as per requirements
            raise Exception(f"SerpAPI request failed: {str(e)}") from e
