#!/usr/bin/env python3
"""Main CLI application for Perplexity Clone - Multi-Agent Search System."""

import sys
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional

from src.config import Config
from src.search.serpapi_client import SerpAPIClient
from src.agents.comprehensive_agent import ComprehensiveAgent


def run_agent(agent, query: str, search_results: List[Dict]) -> Dict[str, str]:
    """Run a single agent and return its response.

    Args:
        agent: Agent instance to run
        query: User query
        search_results: Search results from SerpAPI

    Returns:
        Dict with 'agent_name' and 'response' keys
    """
    try:
        response = agent.process_query(query, search_results)
        return {
            "agent_name": agent.get_strategy_name(),
            "response": response
        }
    except Exception as e:
        # Re-raise to fail fast
        raise Exception(f"{agent.get_strategy_name()} failed: {str(e)}") from e


def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="Perplexity Clone - Multi-Agent Search System"
    )
    parser.add_argument(
        "query",
        nargs="+",
        help="Search query to process"
    )

    args = parser.parse_args()
    query = " ".join(args.query)

    try:
        # Validate configuration
        print("Initializing system...")
        Config.validate()

        # Step 1: Fetch search results (fixed at 7 for speed)
        print(f"\nQuery: {query}")
        print("\n[1/2] Fetching search results...")
        result_count = 7  # Fixed for optimal latency
        serpapi_client = SerpAPIClient()
        search_results = serpapi_client.search(query, num_results=result_count)
        print(f"→ Retrieved {len(search_results)} results")

        # Step 2: Race 3 identical agents - use whoever finishes first
        print("\n[2/2] Racing 3 agents for fastest response...")

        agents = [
            ComprehensiveAgent(),
            ComprehensiveAgent(),
            ComprehensiveAgent()
        ]

        best_response = None
        winner_num = None

        # Don't use context manager - we want to exit immediately when first completes
        executor = ThreadPoolExecutor(max_workers=3)

        try:
            # Submit all agents
            futures = {
                executor.submit(run_agent, agent, query, search_results): i
                for i, agent in enumerate(agents, 1)
            }

            # as_completed() returns futures in order of completion
            # We take the FIRST one that succeeds and exit immediately
            for future in as_completed(futures):
                agent_num = futures[future]
                try:
                    response_data = future.result()
                    best_response = response_data['response']
                    winner_num = agent_num
                    print(f"→ Agent {agent_num} won the race! ⚡")
                    # Immediately shutdown without waiting for other threads
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                except Exception as e:
                    print(f"⚠ Agent {agent_num} failed: {str(e)}")
                    continue

            if best_response is None:
                raise Exception("All agents failed to generate a response")
        finally:
            # Clean up executor if not already shutdown
            if executor._shutdown == False:
                executor.shutdown(wait=False, cancel_futures=True)

        # Display results
        print("\n" + "=" * 80)
        print("ANSWER")
        print("=" * 80)
        print(best_response)
        print("=" * 80)

        # Force exit immediately (don't wait for background threads)
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
