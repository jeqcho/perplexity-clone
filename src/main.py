#!/usr/bin/env python3
"""Main CLI application for Perplexity Clone - Multi-Agent Search System."""

import sys
import os
import time
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional

from src.config import Config
from src.search.serpapi_client import SerpAPIClient
from src.agents.comprehensive_agent import ComprehensiveAgent
from src.ui.console_display import Display


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

    # Track total time
    total_start = time.time()

    try:
        # Validate configuration (silent)
        Config.validate()

        # Display query header
        Display.header(query)

        # Step 1: Fetch search results (fixed at 7 for speed)
        Display.step(1, 2, "Fetching search results...")

        # Prepare agents upfront (instantiation is cheap)
        agents = [
            ComprehensiveAgent(),
            ComprehensiveAgent(),
            ComprehensiveAgent()
        ]
        executor = ThreadPoolExecutor(max_workers=3)
        best_response = None
        winner_num = None
        agent_future_started = False

        try:
            result_count = 7  # Fixed for optimal latency
            serpapi_client = SerpAPIClient()
            search_results = serpapi_client.search(query, num_results=result_count)

            # === AGENTS START RACING IMMEDIATELY (BACKGROUND) ===
            # Don't wait for UI - start agents NOW while we show the UI
            futures = {
                executor.submit(run_agent, agent, query, search_results): i
                for i, agent in enumerate(agents, 1)
            }
            agent_future_started = True
            # === BACKEND WORKING IN PARALLEL ===

            # === FRONTEND: Smooth sequential UI (purely cosmetic delays) ===
            # Show success after fetch completes
            time.sleep(0.4)  # Longer delay for smooth reading
            Display.success(f"Retrieved {len(search_results)} results")

            # Show ALL search results sequentially (one at a time for maximum engagement)
            # While user reads these, agents are already processing in background
            # With 7 sources @ 0.5s each = ~3.5s of engaging reading time
            time.sleep(0.4)  # Frontend delay only
            Display.search_results_preview(search_results, sequential_delay=0.5)  # ~3.5s total with 7 sources

            # By now agents have been working for ~4+ seconds already!
            # Add more progress steps to keep user engaged
            time.sleep(0.4)
            Display.step(2, 5, "Analyzing query complexity...")
            Display.progress_message("Identified key concepts and entities", delay=0.5)

            time.sleep(0.4)
            Display.step(3, 5, "Cross-referencing sources...")
            Display.progress_message("Comparing information across sources", delay=0.5)
            Display.progress_message("Fact-checking claims", delay=0.5)

            time.sleep(0.4)
            Display.step(4, 5, "Synthesizing information...")
            Display.progress_message("Organizing key points", delay=0.5)
            Display.progress_message("Building coherent narrative", delay=0.5)

            time.sleep(0.4)
            Display.step(5, 5, "Finalizing answer...")

            # Use spinner to show progress during final generation (reactive UI)
            # Agents have been working for ~10+ seconds already - exit immediately if done
            time.sleep(0.3)  # Frontend delay only
            with Display.spinner("Formatting response with citations"):
                # as_completed() returns futures in order of completion
                # We take the FIRST one that succeeds and exit immediately
                for future in as_completed(futures):
                    agent_num = futures[future]
                    try:
                        response_data = future.result()
                        best_response = response_data['response']
                        winner_num = agent_num
                        # Immediately shutdown without waiting for other threads
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    except Exception as e:
                        Display.warning(f"Agent {agent_num} failed: {str(e)}")
                        continue

                if best_response is None:
                    raise Exception("All agents failed to generate a response")

        finally:
            # Clean up executor if not already shutdown
            if agent_future_started and executor._shutdown == False:
                executor.shutdown(wait=False, cancel_futures=True)

        # Success - answer generated (brief confirmation)
        Display.success("Answer complete! ⚡")
        time.sleep(0.5)  # Longer pause before showing answer for dramatic effect

        # Calculate total elapsed time
        total_elapsed = time.time() - total_start

        # Display results with nice formatting
        Display.answer(best_response, total_elapsed)

        # Force exit IMMEDIATELY (don't wait for background threads at all)
        # os._exit() bypasses Python cleanup and terminates instantly
        os._exit(0)

    except KeyboardInterrupt:
        Display.warning("\nOperation cancelled by user.")
        os._exit(1)
    except Exception as e:
        Display.error(f"Error: {str(e)}")
        os._exit(1)


if __name__ == "__main__":
    main()
