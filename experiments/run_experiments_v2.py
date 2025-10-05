#!/usr/bin/env python3
"""
Round 2: Test 5 variants of the winning 'structured' prompt + original.

Tests 5 queries × 6 prompts = 30 experiments
Goal: Find the optimal variant of the structured approach
"""

import time
import json
from datetime import datetime
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.config import Config
from src.search.serpapi_client import SerpAPIClient
from src.agents.comprehensive_agent import ComprehensiveAgent
from experiment_queries import TEST_QUERIES, QUERY_DESCRIPTIONS
from experiment_prompts_v2 import SYSTEM_PROMPTS_V2, PROMPT_DESCRIPTIONS_V2


def count_citations(text: str) -> int:
    """Count numbered citations in text."""
    import re
    citations = re.findall(r'\[(\d+)\]', text)
    return len(set(citations))


def count_words(text: str) -> int:
    """Count words in response."""
    return len(text.split())


def has_sections(text: str) -> bool:
    """Check if response has clear section headers."""
    import re
    # Look for markdown headers or emphasized sections
    return bool(re.search(r'(^|\n)(#{1,3}\s|[A-Z][^.!?]*:|\*\*[A-Z])', text))


def has_bullets(text: str) -> bool:
    """Check if response uses bullet points."""
    return bool('- ' in text or '• ' in text or '* ' in text)


def has_tables(text: str) -> bool:
    """Check if response uses tables."""
    return bool('|' in text and '---' in text)


def has_emojis(text: str) -> bool:
    """Check if response uses emojis."""
    import re
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return bool(emoji_pattern.search(text))


def run_single_experiment(
    query: str,
    search_results: List[Dict],
    system_prompt: str,
    prompt_name: str
) -> Dict:
    """Run a single experiment and measure metrics."""

    class CustomAgent(ComprehensiveAgent):
        def get_system_prompt(self):
            return system_prompt

    agent = CustomAgent()
    start_time = time.time()

    try:
        response = agent.process_query(query, search_results)
        latency = time.time() - start_time

        metrics = {
            "success": True,
            "latency_seconds": round(latency, 2),
            "word_count": count_words(response),
            "citation_count": count_citations(response),
            "has_citation_list": "Citations:" in response or "Citation" in response,
            "has_sections": has_sections(response),
            "has_bullets": has_bullets(response),
            "has_tables": has_tables(response),
            "has_emojis": has_emojis(response),
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
            "has_sections": False,
            "has_bullets": False,
            "has_tables": False,
            "has_emojis": False,
            "response_preview": "",
            "full_response": "",
            "error": str(e)
        }

    return metrics


def run_all_experiments():
    """Run all experiments."""
    print("=" * 80)
    print("ROUND 2: STRUCTURED PROMPT OPTIMIZATION")
    print("=" * 80)
    print(f"\nStarting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nQueries: {len(TEST_QUERIES)}")
    print(f"Prompt variants: {len(SYSTEM_PROMPTS_V2)}")
    print(f"Total experiments: {len(TEST_QUERIES) * len(SYSTEM_PROMPTS_V2)}")
    print("\n" + "=" * 80 + "\n")

    Config.validate()

    # Reuse search results from Round 1 if available
    print("Fetching search results...")
    serpapi_client = SerpAPIClient()
    query_results = {}

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"  [{i}/{len(TEST_QUERIES)}] {QUERY_DESCRIPTIONS[i-1]}")
        query_results[query] = serpapi_client.search(query, num_results=7)
        time.sleep(0.5)

    print(f"\n✓ Search results fetched\n")
    print("=" * 80 + "\n")

    # Prepare tasks
    tasks = []
    for query_idx, query in enumerate(TEST_QUERIES):
        for prompt_name, system_prompt in SYSTEM_PROMPTS_V2.items():
            tasks.append({
                "query": query,
                "query_idx": query_idx,
                "prompt_name": prompt_name,
                "system_prompt": system_prompt,
                "search_results": query_results[query]
            })

    total = len(tasks)
    print(f"Running {total} experiments in parallel (max 5 concurrent)...\n")

    results = []
    completed = 0

    def run_task(task):
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
            "prompt_description": PROMPT_DESCRIPTIONS_V2[task["prompt_name"]],
            **metrics
        }

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(run_task, task): task for task in tasks}

        for future in as_completed(futures):
            task = futures[future]
            result = future.result()
            results.append(result)
            completed += 1

            query_desc = QUERY_DESCRIPTIONS[task["query_idx"]][:25]
            prompt_name = task["prompt_name"]

            if result["success"]:
                format_icons = ""
                if result["has_bullets"]: format_icons += "•"
                if result["has_tables"]: format_icons += "⊞"
                if result["has_emojis"]: format_icons += "🎨"
                print(f"[{completed}/{total}] ✓ {query_desc:25} | {prompt_name:20} | {result['latency_seconds']:5.2f}s | {result['word_count']:4d}w | {result['citation_count']:2d}c | {format_icons}")
            else:
                print(f"[{completed}/{total}] ✗ {query_desc:25} | {prompt_name:20} | FAILED")

    # Save results
    output_file = f"experiment_results_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'=' * 80}")
    print(f"✓ Round 2 complete!")
    print(f"Results saved to: {output_file}")
    print(f"{'=' * 80}\n")

    return results, output_file


def generate_markdown_report(results: List[Dict], output_file: str):
    """Generate Round 2 markdown report."""

    report = f"""# Round 2: Structured Prompt Optimization Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Experiments:** {len(results)}
**Goal:** Optimize the winning 'structured' prompt from Round 1

---

## Variants Tested

"""

    for name, desc in PROMPT_DESCRIPTIONS_V2.items():
        report += f"- **{name}**: {desc}\n"

    report += "\n---\n\n## Overall Performance Comparison\n\n"

    # Calculate stats
    prompt_stats = {}
    for prompt_name in SYSTEM_PROMPTS_V2.keys():
        prompt_results = [r for r in results if r['prompt_name'] == prompt_name and r['success']]
        if prompt_results:
            prompt_stats[prompt_name] = {
                "avg_latency": sum(r['latency_seconds'] for r in prompt_results) / len(prompt_results),
                "avg_words": sum(r['word_count'] for r in prompt_results) / len(prompt_results),
                "avg_citations": sum(r['citation_count'] for r in prompt_results) / len(prompt_results),
                "bullets_pct": sum(1 for r in prompt_results if r['has_bullets']) / len(prompt_results),
                "tables_pct": sum(1 for r in prompt_results if r['has_tables']) / len(prompt_results),
                "emojis_pct": sum(1 for r in prompt_results if r['has_emojis']) / len(prompt_results),
            }

    report += "| Variant | Avg Latency | Avg Words | Avg Citations | Bullets | Tables | Emojis |\n"
    report += "|---------|-------------|-----------|---------------|---------|--------|--------|\n"

    for name, stats in sorted(prompt_stats.items(), key=lambda x: x[1]['avg_latency']):
        report += f"| **{name}** | {stats['avg_latency']:.2f}s | {stats['avg_words']:.0f} | {stats['avg_citations']:.1f} | {stats['bullets_pct']*100:.0f}% | {stats['tables_pct']*100:.0f}% | {stats['emojis_pct']*100:.0f}% |\n"

    report += "\n---\n\n## Performance by Query Type\n\n"

    for query_idx, query_type in enumerate(QUERY_DESCRIPTIONS):
        report += f"### {query_idx + 1}. {query_type}\n\n"
        query_results = [r for r in results if r['query_type'] == query_type and r['success']]

        if query_results:
            report += "| Variant | Latency | Words | Citations | Format |\n"
            report += "|---------|---------|-------|-----------|--------|\n"

            for r in sorted(query_results, key=lambda x: x['latency_seconds']):
                formats = []
                if r['has_bullets']: formats.append("bullets")
                if r['has_tables']: formats.append("tables")
                if r['has_emojis']: formats.append("emojis")
                format_str = ", ".join(formats) if formats else "prose"

                report += f"| {r['prompt_name']} | {r['latency_seconds']:.2f}s | {r['word_count']} | {r['citation_count']} | {format_str} |\n"

        report += "\n"

    # Find winners
    fastest = min(prompt_stats.items(), key=lambda x: x[1]['avg_latency'])
    most_citations = max(prompt_stats.items(), key=lambda x: x[1]['avg_citations'])
    most_concise = min(prompt_stats.items(), key=lambda x: x[1]['avg_words'])

    report += f"""---

## Key Findings

### Speed Champion 🏆
**{fastest[0]}** - {fastest[1]['avg_latency']:.2f}s average

### Citation Champion 📚
**{most_citations[0]}** - {most_citations[1]['avg_citations']:.1f} citations average

### Brevity Champion 📝
**{most_concise[0]}** - {most_concise[1]['avg_words']:.0f} words average

---

## Comparison to Round 1 Winner

**Round 1 Structured Prompt:**
- Latency: 21.43s
- Words: 498
- Citations: 6.8

**Best Round 2 Variant ({fastest[0]}):**
- Latency: {fastest[1]['avg_latency']:.2f}s ({((fastest[1]['avg_latency'] - 21.43) / 21.43 * 100):+.1f}% vs Round 1)
- Words: {fastest[1]['avg_words']:.0f} ({((fastest[1]['avg_words'] - 498) / 498 * 100):+.1f}% vs Round 1)
- Citations: {fastest[1]['avg_citations']:.1f} ({((fastest[1]['avg_citations'] - 6.8) / 6.8 * 100):+.1f}% vs Round 1)

---

## Recommendations

See full responses in `{output_file}` to make final decision.

---

*Generated by run_experiments_v2.py*
"""

    report_file = output_file.replace('.json', '_report.md')
    with open(report_file, 'w') as f:
        f.write(report)

    print(f"📊 Report generated: {report_file}\n")
    return report_file


if __name__ == "__main__":
    results, output_file = run_all_experiments()
    report_file = generate_markdown_report(results, output_file)

    print(f"\n{'=' * 80}")
    print("📁 Round 2 files:")
    print(f"  - {output_file}")
    print(f"  - {report_file}")
    print(f"{'=' * 80}\n")
