#!/usr/bin/env python3
"""
Run prompt optimization experiments.

Tests 5 queries × 5 prompts = 25 experiments
Measures: latency, token count, citation quality, response quality
"""

import time
import json
from datetime import datetime
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.config import Config
from src.search.serpapi_client import SerpAPIClient
from src.agents.comprehensive_agent import ComprehensiveAgent
from src.llm.openai_client import OpenAIClient
from experiment_queries import TEST_QUERIES, QUERY_DESCRIPTIONS
from experiment_prompts import SYSTEM_PROMPTS, PROMPT_DESCRIPTIONS


def count_citations(text: str) -> int:
    """Count numbered citations in text."""
    import re
    citations = re.findall(r'\[(\d+)\]', text)
    return len(set(citations))  # Unique citations


def count_words(text: str) -> int:
    """Count words in response."""
    return len(text.split())


def run_single_experiment(
    query: str,
    search_results: List[Dict],
    system_prompt: str,
    prompt_name: str
) -> Dict:
    """Run a single experiment and measure metrics."""

    # Create agent with custom system prompt
    class CustomAgent(ComprehensiveAgent):
        def get_system_prompt(self):
            return system_prompt

    agent = CustomAgent()

    # Time the response
    start_time = time.time()

    try:
        response = agent.process_query(query, search_results)
        latency = time.time() - start_time

        # Calculate metrics
        metrics = {
            "success": True,
            "latency_seconds": round(latency, 2),
            "word_count": count_words(response),
            "citation_count": count_citations(response),
            "has_citation_list": "Citations:" in response or "Citation" in response,
            "response_preview": response[:200] + "..." if len(response) > 200 else response,
            "full_response": response,
            "error": None
        }
    except Exception as e:
        metrics = {
            "success": False,
            "latency_seconds": round(time.time() - start_time, 2),
            "word_count": 0,
            "citation_count": 0,
            "has_citation_list": False,
            "response_preview": "",
            "full_response": "",
            "error": str(e)
        }

    return metrics


def run_all_experiments():
    """Run all 25 experiments (5 queries × 5 prompts)."""
    print("=" * 80)
    print("PROMPT OPTIMIZATION EXPERIMENTS")
    print("=" * 80)
    print(f"\nStarting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nQueries: {len(TEST_QUERIES)}")
    print(f"Prompts: {len(SYSTEM_PROMPTS)}")
    print(f"Total experiments: {len(TEST_QUERIES) * len(SYSTEM_PROMPTS)}")
    print("\n" + "=" * 80 + "\n")

    # Validate config
    Config.validate()

    # Fetch search results for all queries ONCE (to be fair)
    print("Fetching search results for all queries...")
    serpapi_client = SerpAPIClient()
    query_results = {}

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"  [{i}/{len(TEST_QUERIES)}] {QUERY_DESCRIPTIONS[i-1]}")
        query_results[query] = serpapi_client.search(query, num_results=7)
        time.sleep(0.5)  # Rate limiting

    print(f"\n✓ All search results fetched\n")
    print("=" * 80 + "\n")

    # Prepare all experiment tasks
    tasks = []
    for query_idx, query in enumerate(TEST_QUERIES):
        for prompt_name, system_prompt in SYSTEM_PROMPTS.items():
            tasks.append({
                "query": query,
                "query_idx": query_idx,
                "prompt_name": prompt_name,
                "system_prompt": system_prompt,
                "search_results": query_results[query]
            })

    total = len(tasks)
    print(f"Running {total} experiments in parallel (max 5 concurrent)...\n")

    # Run experiments in parallel
    results = []
    completed = 0

    def run_task(task):
        """Wrapper to run experiment with task metadata."""
        metrics = run_single_experiment(
            query=task["query"],
            search_results=task["search_results"],
            system_prompt=task["system_prompt"],
            prompt_name=task["prompt_name"]
        )
        return {
            "query": task["query"],
            "query_type": QUERY_DESCRIPTIONS[task["query_idx"]],
            "prompt_name": task["prompt_name"],
            "prompt_description": PROMPT_DESCRIPTIONS[task["prompt_name"]],
            **metrics
        }

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(run_task, task): task for task in tasks}

        for future in as_completed(futures):
            task = futures[future]
            result = future.result()
            results.append(result)
            completed += 1

            query_desc = QUERY_DESCRIPTIONS[task["query_idx"]][:30]
            prompt_name = task["prompt_name"]

            if result["success"]:
                print(f"[{completed}/{total}] ✓ {query_desc:30} | {prompt_name:12} | {result['latency_seconds']:5.2f}s | {result['word_count']:4d}w | {result['citation_count']:2d}c")
            else:
                print(f"[{completed}/{total}] ✗ {query_desc:30} | {prompt_name:12} | FAILED: {result['error'][:30]}")

    # Save results
    output_file = f"experiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'=' * 80}")
    print(f"✓ All experiments complete!")
    print(f"Results saved to: {output_file}")
    print(f"{'=' * 80}\n")

    return results, output_file


def generate_markdown_report(results: List[Dict], output_file: str):
    """Generate a markdown report from experiment results."""

    report = f"""# Prompt Optimization Experiment Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Experiments:** {len(results)}
**Data File:** `{output_file}`

---

## Executive Summary

This report analyzes **5 system prompts** across **5 query types** (25 total experiments) to optimize the perplexity-clone system for speed, quality, and citation accuracy.

### Query Types Tested
"""

    for i, desc in enumerate(QUERY_DESCRIPTIONS, 1):
        report += f"{i}. **{desc}**: `{TEST_QUERIES[i-1][:60]}...`\n"

    report += "\n### Prompt Strategies Tested\n\n"

    for name, desc in PROMPT_DESCRIPTIONS.items():
        report += f"- **{name}**: {desc}\n"

    report += "\n---\n\n## Overall Performance Comparison\n\n"

    # Calculate averages per prompt
    prompt_stats = {}
    for prompt_name in SYSTEM_PROMPTS.keys():
        prompt_results = [r for r in results if r['prompt_name'] == prompt_name and r['success']]
        if prompt_results:
            prompt_stats[prompt_name] = {
                "avg_latency": sum(r['latency_seconds'] for r in prompt_results) / len(prompt_results),
                "avg_words": sum(r['word_count'] for r in prompt_results) / len(prompt_results),
                "avg_citations": sum(r['citation_count'] for r in prompt_results) / len(prompt_results),
                "success_rate": len(prompt_results) / len([r for r in results if r['prompt_name'] == prompt_name]),
                "citation_list_rate": sum(1 for r in prompt_results if r['has_citation_list']) / len(prompt_results)
            }

    report += "| Prompt | Avg Latency | Avg Words | Avg Citations | Success Rate | Citation List % |\n"
    report += "|--------|-------------|-----------|---------------|--------------|----------------|\n"

    for name, stats in sorted(prompt_stats.items(), key=lambda x: x[1]['avg_latency']):
        report += f"| **{name}** | {stats['avg_latency']:.2f}s | {stats['avg_words']:.0f} | {stats['avg_citations']:.1f} | {stats['success_rate']*100:.0f}% | {stats['citation_list_rate']*100:.0f}% |\n"

    report += "\n---\n\n## Performance by Query Type\n\n"

    for query_idx, query_type in enumerate(QUERY_DESCRIPTIONS):
        report += f"### {query_idx + 1}. {query_type}\n\n"
        report += f"**Query:** `{TEST_QUERIES[query_idx]}`\n\n"

        query_results = [r for r in results if r['query_type'] == query_type and r['success']]

        if query_results:
            report += "| Prompt | Latency | Words | Citations | Preview |\n"
            report += "|--------|---------|-------|-----------|----------|\n"

            for r in sorted(query_results, key=lambda x: x['latency_seconds']):
                preview = r['response_preview'].replace('\n', ' ')[:60]
                report += f"| {r['prompt_name']} | {r['latency_seconds']:.2f}s | {r['word_count']} | {r['citation_count']} | {preview}... |\n"

        report += "\n"

    report += "---\n\n## Key Findings\n\n"

    # Find best performers
    fastest = min(prompt_stats.items(), key=lambda x: x[1]['avg_latency'])
    most_concise = min(prompt_stats.items(), key=lambda x: x[1]['avg_words'])
    most_citations = max(prompt_stats.items(), key=lambda x: x[1]['avg_citations'])

    report += f"""
### Speed Champion 🏆
**{fastest[0]}** - Average latency: **{fastest[1]['avg_latency']:.2f}s**

### Brevity Champion 📝
**{most_concise[0]}** - Average words: **{most_concise[1]['avg_words']:.0f}**

### Citation Champion 📚
**{most_citations[0]}** - Average citations: **{most_citations[1]['avg_citations']:.1f}**

---

## Recommendations

Based on the experimental results:

1. **For Speed-First Applications**: Use `{fastest[0]}` prompt
2. **For Concise Answers**: Use `{most_concise[0]}` prompt
3. **For Well-Cited Responses**: Use `{most_citations[0]}` prompt

### Next Steps
- Review full responses in `{output_file}`
- Consider A/B testing top 2 prompts in production
- Iterate on winning prompt for further optimization

---

*Generated by prompt_optimization_experiments.py*
"""

    report_file = output_file.replace('.json', '_report.md')
    with open(report_file, 'w') as f:
        f.write(report)

    print(f"📊 Markdown report generated: {report_file}\n")
    return report_file


if __name__ == "__main__":
    results, output_file = run_all_experiments()
    report_file = generate_markdown_report(results, output_file)

    print(f"\n{'=' * 80}")
    print("📁 Files generated:")
    print(f"  - {output_file} (raw JSON data)")
    print(f"  - {report_file} (markdown report)")
    print(f"{'=' * 80}\n")
