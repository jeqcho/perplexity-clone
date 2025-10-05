# Perplexity Clone - Speed-Optimized Multi-Agent Search

A **latency-first** search system that races 3 parallel LLM agents and returns the fastest response with citations. **Optimized through 55 experiments** to deliver maximum speed and user satisfaction.

## Architecture

This system uses a **racing multi-agent architecture** optimized for minimum latency:

1. **Search Engine**: Fetches 7 Google search results via SerpAPI (fixed for optimal speed)
2. **Racing Agents**: 3 identical agents process the query **in parallel** — **first one to finish wins** ⚡
   - All use the same **optimized prompt** (tested against 11 variants)
   - Runs simultaneously using ThreadPoolExecutor
   - System exits immediately when first agent completes
   - Typical response time: **~19 seconds** (31% faster than baseline)

**Performance Metrics:**
- ⚡ **19.42s average latency** (optimized through testing)
- 📝 **322 words average** (50% more concise than baseline)
- 📚 **6.4 citations** (high trust and verifiability)
- ⭐ **5/5 user satisfaction** (based on subjective analysis)

**Why this design?**
- ✅ **Speed**: Optimized prompt + racing = fastest responses
- ✅ **Scannability**: Section headers and bullets for easy reading
- ✅ **Reliability**: If one agent fails/times out, others continue
- ✅ **Simple**: No complex judging logic that adds latency
- ✅ **Cost-effective**: 50% fewer tokens than verbose approaches

All agents use LLMs via OpenRouter (configurable model) and return **structured answers** with section headers and numbered citations `[1], [2]`.

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

1. **Search**: Fetches 7 Google search results using SerpAPI (optimized fixed count)

2. **Racing Agents**: Three identical agents process the search results in parallel
   - All use the **v2_sections** prompt (winner of 55 experiments)
   - Each agent races to complete first
   - ThreadPoolExecutor runs all 3 simultaneously

3. **First to Finish Wins**: System immediately returns the first completed response
   - No waiting for slower agents
   - No complex judging logic (speed-first design)
   - Other agents are cancelled to save resources

4. **Output**: Structured response with section headers and numbered citations

**Response Format:**
```
## Direct Answer
[One-sentence answer with citation]

## Key Points
- [Bullet 1 with citation]
- [Bullet 2 with citation]
...

## Citations
[1] Source title - URL
[2] Source title - URL
```

## Error Handling

The system follows a "fail fast" approach:
- API failures (OpenAI, SerpAPI) immediately throw exceptions
- Invalid configurations are caught at startup
- All errors include descriptive messages

## Prompt Optimization Journey

This system was **scientifically optimized through 55 experiments** testing 11 different prompt strategies:

### Round 1: Approach Comparison (25 experiments)
Tested 5 different approaches across 5 query types:
- **Baseline** (comprehensive prose)
- **Concise** (ultra-brief)
- **Structured** (bullets/tables) ← **WINNER**
- **Analytical** (deep reasoning)
- **Hybrid** (adaptive)

**Result:** Structured approach won on speed (21.43s) and user preference

### Round 2: Structured Optimization (30 experiments)
Tested 6 variants of the structured approach:
- **v1_minimal** (ultra-concise)
- **v2_sections** (section headers) ← **WINNER**
- **v3_tables** (table-optimized)
- **v4_visual** (emoji markers)
- **v5_adaptive** (query-adaptive)
- **structured_original** (Round 1 baseline)

**Result:** v2_sections won on speed (19.42s), user satisfaction (5/5), and scannability

### Final Performance Gains
| Metric | Before Optimization | After Optimization | Improvement |
|--------|-------------------|-------------------|-------------|
| Speed | 28.27s | **19.42s** | **+31% faster** |
| Word Count | 647 | **322** | **+50% more concise** |
| User Rating | 3/5 | **5/5** | **Perfect score** |
| Citations | 6.2 | **6.4** | **+3% better** |

**See full analysis:**
- [experiments/FINAL_PROMPT_RECOMMENDATION.md](experiments/FINAL_PROMPT_RECOMMENDATION.md) - Complete optimization journey
- [experiments/README.md](experiments/README.md) - Experiment overview and methodology
- [experiments/round2_subjective_analysis.md](experiments/round2_subjective_analysis.md) - User preference analysis

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
