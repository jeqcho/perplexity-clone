# Perplexity Clone - Speed-Optimized Multi-Agent Search

A **latency-first** search system that races 3 parallel LLM agents and returns the fastest response with citations. Built for speed over everything else.

## Architecture

This system uses a **racing multi-agent architecture** optimized for minimum latency:

1. **Query Analyzer**: LLM determines optimal number of search results (5-10) based on query complexity
2. **Search Engine**: Fetches Google search results via SerpAPI
3. **Racing Agents**: 3 identical agents process the query **in parallel** — **first one to finish wins** ⚡
   - All agents use the same comprehensive prompt
   - Runs simultaneously using ThreadPoolExecutor
   - Remaining agents are cancelled once winner completes
   - Typical speedup: **3x faster** than sequential processing

**Why this design?**
- ✅ **Speed**: First response typically arrives in ~3-5 seconds
- ✅ **Reliability**: If one agent fails/times out, others continue
- ✅ **Simple**: No complex judging logic that adds latency
- ✅ **Cost-effective**: Cancels redundant API calls after first completion

All agents use LLMs via OpenRouter (configurable model) and return answers with numbered citations `[1], [2]`.

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- [OpenRouter](https://openrouter.ai/) API key (for LLM access)
- [SerpAPI](https://serpapi.com/) key (for Google search)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd perplexity-clone
```

2. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini  # Or any model from https://openrouter.ai/models
SERPAPI_KEY=your_serpapi_key_here
```

3. Install globally with uv:
```bash
uv tool install --editable .
```

This installs the `perp` command globally, so you can use it from anywhere without needing `uv run`.

## Usage

### Basic Usage

Run a query from the command line:

```bash
perp "What are the latest developments in quantum computing?"
```

Or use the full command name:

```bash
perplexity "What are the latest developments in quantum computing?"
```

### Example Output

```
Initializing system...

Query: What are the latest developments in quantum computing?

[1/3] Analyzing query complexity...
→ Will fetch 7 search results

[2/3] Fetching search results...
→ Retrieved 6 results

[3/3] Racing 3 agents for fastest response...
→ Agent 2 won the race! ⚡

================================================================================
ANSWER
================================================================================
Recent developments in quantum computing have focused on error correction and
practical applications. Google's quantum processor achieved quantum advantage
with 70 qubits [1], while IBM announced a 1,121-qubit quantum processor [2]...

Citations:
[1] Google Quantum AI achieves breakthrough - https://...
[2] IBM Unveils Quantum Processor - https://...
================================================================================
```

## Project Structure

```
perplexity-clone/
├── .env.example              # Template for API keys
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── src/
    ├── main.py              # CLI entry point
    ├── config.py            # Configuration management
    ├── search/
    │   ├── serpapi_client.py    # SerpAPI integration
    │   └── result_analyzer.py   # Query complexity analysis
    ├── agents/
    │   ├── base_agent.py        # Abstract base class
    │   ├── comprehensive_agent.py  # Broad coverage strategy
    │   ├── factual_agent.py        # Fact-focused strategy
    │   └── analytical_agent.py     # Deep analysis strategy
    ├── judge/
    │   └── llm_judge.py         # Response evaluation
    ├── llm/
    │   └── openai_client.py     # GPT-5-nano integration
    └── utils/
        ├── citation_formatter.py  # Citation formatting
        └── response_validator.py  # Response validation
```

## How It Works

1. **Query Analysis**: The system first analyzes your query to determine how many search results would be optimal (5-10 based on complexity)

2. **Search**: Fetches Google search results using SerpAPI

3. **Parallel Processing**: Three agents process the same search results simultaneously, each with a different strategy:
   - Comprehensive: Broad, well-rounded coverage
   - Factual: Hard facts and statistics
   - Analytical: Deep insights and reasoning

4. **Judging**: An LLM judge evaluates all responses based on:
   - Accuracy of information
   - Quality of citations
   - Coherence and clarity
   - Completeness of answer
   - Relevance to query

5. **Output**: The best response is selected and displayed with numbered citations

## Error Handling

The system follows a "fail fast" approach:
- API failures (OpenAI, SerpAPI) immediately throw exceptions
- Invalid configurations are caught at startup
- All errors include descriptive messages

## Future Enhancements

### Supabase Caching Implementation

To reduce API costs and improve response times, a caching layer can be added using Supabase:

**Configuration** (already in .env.example):
```env
SUPABASE_URL=https://tfvenxrnmdxbbnvidaut.supabase.co
SUPABASE_KEY=<your-supabase-anon-key>
```

**Implementation Plan**:

1. **Database Schema**:
```sql
CREATE TABLE query_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query_hash TEXT UNIQUE NOT NULL,
  query_text TEXT NOT NULL,
  response TEXT NOT NULL,
  search_results JSONB,
  agent_responses JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '1 hour'
);

CREATE INDEX idx_query_hash ON query_cache(query_hash);
CREATE INDEX idx_expires_at ON query_cache(expires_at);
```

2. **Cache Module** (src/cache/supabase_cache.py):
```python
import hashlib
from datetime import datetime, timedelta
from supabase import create_client
from src.config import Config

class QueryCache:
    def __init__(self):
        self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

    def get(self, query: str):
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        result = self.client.table('query_cache')\
            .select('*')\
            .eq('query_hash', query_hash)\
            .gt('expires_at', datetime.now().isoformat())\
            .single()\
            .execute()
        return result.data if result.data else None

    def set(self, query: str, response: str, metadata: dict):
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        self.client.table('query_cache').upsert({
            'query_hash': query_hash,
            'query_text': query,
            'response': response,
            'search_results': metadata.get('search_results'),
            'agent_responses': metadata.get('agent_responses'),
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
        }).execute()
```

3. **Integration in main.py**:
- Check cache before running agents
- Store results after judge selection
- Add TTL of 1 hour for cached responses

4. **Cleanup Job** (optional):
```sql
-- Run periodically to remove expired entries
DELETE FROM query_cache WHERE expires_at < NOW();
```

**Benefits**:
- Instant responses for repeated queries
- Reduced API costs (no duplicate LLM calls)
- Store full agent responses for analysis
- 1-hour TTL ensures fresh data for time-sensitive queries

To implement, uncomment Supabase configuration in .env and add the cache module following the plan above.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
