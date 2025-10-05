"""Test queries for prompt optimization experiments."""

# 5 diverse queries from simple to complex
TEST_QUERIES = [
    # 1. Simple factual - single answer
    "What is the capital of France?",

    # 2. Moderate factual - requires synthesis
    "What are the health benefits of green tea?",

    # 3. Current events - needs recent info
    "What are the latest developments in AI regulation?",

    # 4. Complex analytical - requires comparison
    "Compare the economic impacts of remote work on cities versus rural areas",

    # 5. Multi-faceted technical - requires depth + breadth
    "Explain how quantum entanglement works and its applications in quantum computing",
]

QUERY_DESCRIPTIONS = [
    "Simple factual (single answer)",
    "Moderate factual (synthesis)",
    "Current events (recent info)",
    "Complex analytical (comparison)",
    "Multi-faceted technical (depth + breadth)"
]
