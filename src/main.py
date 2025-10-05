#!/usr/bin/env python3
"""Main CLI application for Perplexity Clone - Multi-Agent Search System."""

import sys
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from src.config import Config
from src.search.serpapi_client import SerpAPIClient
from src.search.result_analyzer import ResultAnalyzer
from src.agents.comprehensive_agent import ComprehensiveAgent
from src.agents.factual_agent import FactualAgent
from src.agents.analytical_agent import AnalyticalAgent
from src.judge.llm_judge import LLMJudge
from src.utils.response_validator import ResponseValidator


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
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output including all agent responses"
    )

    args = parser.parse_args()
    query = " ".join(args.query)

    try:
        # Validate configuration
        print("Initializing system...")
        Config.validate()

        # Step 1: Analyze query to determine optimal number of search results
        print(f"\nQuery: {query}")
        print("\n[1/5] Analyzing query complexity...")
        analyzer = ResultAnalyzer()
        result_count = analyzer.determine_result_count(query)
        print(f"→ Will fetch {result_count} search results")

        # Step 2: Fetch search results
        print("\n[2/5] Fetching search results...")
        serpapi_client = SerpAPIClient()
        search_results = serpapi_client.search(query, num_results=result_count)
        print(f"→ Retrieved {len(search_results)} results")

        # Step 3: Run agents in parallel
        print("\n[3/5] Running agents in parallel...")
        agents = [
            ComprehensiveAgent(),
            FactualAgent(),
            AnalyticalAgent()
        ]

        agent_responses = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(run_agent, agent, query, search_results): agent
                for agent in agents
            }

            for future in as_completed(futures):
                agent = futures[future]
                try:
                    response_data = future.result()
                    agent_responses.append(response_data)
                    print(f"→ {response_data['agent_name']} completed")
                except Exception as e:
                    # Fail fast on agent errors
                    raise e

        # Step 4: Validate responses (optional, for debugging)
        if args.verbose:
            print("\n[4/5] Validating responses...")
            validation = ResponseValidator.validate_all_responses(agent_responses)
            if not validation["valid"]:
                print("⚠ Warning: Some validation issues found:")
                for issue in validation["issues"]:
                    print(f"  - {issue}")
            else:
                print("→ All responses valid")
        else:
            print("\n[4/5] Validating responses...")
            print("→ Validation complete")

        # Step 5: Judge selects best response
        print("\n[5/5] Judging responses...")
        judge = LLMJudge()
        best_response = judge.evaluate_responses(query, agent_responses)
        print("→ Best response selected")

        # Display results
        print("\n" + "=" * 80)
        print("ANSWER")
        print("=" * 80)
        print(best_response)
        print("=" * 80)

        # Verbose output: show all agent responses
        if args.verbose:
            print("\n" + "=" * 80)
            print("ALL AGENT RESPONSES (VERBOSE MODE)")
            print("=" * 80)
            for response_data in agent_responses:
                print(f"\n{response_data['agent_name']}:")
                print("-" * 80)
                print(response_data['response'])
                print("-" * 80)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
