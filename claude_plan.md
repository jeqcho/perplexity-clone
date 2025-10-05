## Perplexity Clone - Advanced Implementation Plan

### Technology Stack
- **Package Manager**: `uv` (fast Python dependency management)
- **Search API**: SerpAPI (`/search` endpoint with `q`, `api_key`, `num` parameters)
- **LLM Providers**: Multiple (OpenAI GPT-4, Anthropic Claude, etc.)
- **Database**: Supabase (PostgreSQL-based caching)
- **CLI**: `rich` library for beautiful terminal UI

### Architecture: Multi-Agent with LLM Judge

**Core Flow**: Query → Cache Check → [Miss: Search → Parallel Agents → Judge] → Cache Store → Display

### Implementation Steps

#### 1. Save Implementation Plan
- Create `IMPLEMENTATION_PLAN.md` with full architecture details

#### 2. Project Setup (`uv`)
- `uv init` project structure
- Add dependencies: `openai`, `anthropic`, `google-search-results`, `supabase`, `rich`, `python-dotenv`
- Create `.env.example` template
- `.gitignore` for sensitive files

#### 3. SerpAPI Integration Module
- Use `GoogleSearch` client from `google-search-results` package
- Fetch `organic_results` array: `title`, `link`, `snippet`, `position`
- Parse top 5-10 results into structured context

#### 4. Multi-Agent System (Parallel Execution)
- Create 3-5 agent variants with different strategies:
  - Agent 1: OpenAI GPT-4 with numbered citations
  - Agent 2: Anthropic Claude with footnote style
  - Agent 3: Alternative prompting strategies
  - Agent 4: Different context formatting
- Use `asyncio.gather()` for parallel execution

#### 5. LLM Judge System
- Judge LLM evaluates responses on:
  - Citation accuracy (1-10)
  - Answer relevance (1-10)
  - Source diversity (1-10)
  - Response clarity (1-10)
- Returns best response + reasoning

#### 6. Supabase Caching Layer
- Schema: `queries` table with query_hash, response, sources, metadata
- Hash queries (normalized)
- 1-hour TTL on cache
- Cache hit/miss tracking

#### 7. CLI Interface (Rich)
- Input prompts with formatting
- Loading indicators for each step
- Formatted output with citations + sources
- Error handling

#### 8. Main Application Flow
- Integrate all modules
- CLI entry point
- Error handling & logging