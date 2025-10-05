# Prompt Optimization Experiments

This directory contains all experimental data and code from the scientific prompt optimization process.

**Total Experiments:** 55 (Round 1: 25 + Round 2: 30)
**Prompts Tested:** 11 different strategies
**Winner:** `v2_sections` (section headers prompt)

---

## 📊 Quick Start

**Read this first:** [FINAL_PROMPT_RECOMMENDATION.md](FINAL_PROMPT_RECOMMENDATION.md)

This is the comprehensive summary of all experiments with the final recommendation and implementation guide.

---

## 📁 Directory Structure

```
experiments/
├── README.md                           # This file
├── FINAL_PROMPT_RECOMMENDATION.md      # ⭐ START HERE - Final analysis & winner
│
├── round1/                             # Round 1: Approach comparison
│   ├── experiment_results_20251005_165514.json
│   └── experiment_results_20251005_165514_report.md
│
├── round2/                             # Round 2: Structured optimization
│   ├── experiment_results_v2_20251005_170320.json
│   └── experiment_results_v2_20251005_170320_report.md
│
├── subjective_analysis.md              # Round 1 user preference analysis
├── round2_subjective_analysis.md       # Round 2 user preference analysis
│
├── experiment_queries.py               # 5 test queries (simple → complex)
├── experiment_prompts.py               # Round 1 prompt definitions
├── experiment_prompts_v2.py            # Round 2 prompt variants
├── run_experiments.py                  # Round 1 experiment runner
└── run_experiments_v2.py               # Round 2 experiment runner
```

---

## 🏆 Results Summary

### Round 1: Approach Comparison (25 experiments)

**Goal:** Find the best overall approach

**Tested:**
1. Baseline (comprehensive prose)
2. Concise (ultra-brief)
3. **Structured (bullets/tables)** ← Winner
4. Analytical (deep reasoning)
5. Hybrid (adaptive)

**Winner:** Structured
- Speed: 21.43s average
- Words: 498
- Citations: 6.8
- User rating: ⭐⭐⭐⭐ (4/5)

---

### Round 2: Structured Optimization (30 experiments)

**Goal:** Optimize the structured approach

**Tested:**
1. v1_minimal (ultra-concise)
2. **v2_sections (section headers)** ← Winner
3. v3_tables (table-optimized)
4. v4_visual (emoji markers)
5. v5_adaptive (query-adaptive)
6. structured_original (Round 1 baseline)

**Winner:** v2_sections
- Speed: 19.42s average (**9% faster than Round 1**)
- Words: 322 (**35% more concise than Round 1**)
- Citations: 6.4
- User rating: ⭐⭐⭐⭐⭐ (5/5)

---

## 📈 Performance Gains

| Metric | Original | Round 1 Winner | **Final Winner** | Total Gain |
|--------|----------|----------------|-----------------|------------|
| Speed | 28.27s | 21.43s | **19.42s** | **+31%** |
| Words | 647 | 498 | **322** | **+50%** |
| Citations | 6.2 | 6.8 | **6.4** | **+3%** |
| User Rating | 3/5 | 4/5 | **5/5** | **Perfect** |

---

## 🔬 Experiment Methodology

### Queries Tested (5 types)
1. **Simple factual:** "What is the capital of France?"
2. **Moderate synthesis:** "What are the health benefits of green tea?"
3. **Current events:** "What are the latest developments in AI regulation?"
4. **Complex comparison:** "Compare economic impacts of remote work..."
5. **Technical depth:** "Explain quantum entanglement and applications..."

### Metrics Measured

**Quantitative:**
- Latency (seconds)
- Word count
- Citation count
- Format features (bullets, tables, emojis)

**Qualitative (Subjective Analysis):**
- User preference ratings (1-5 stars)
- Scannability
- Appropriate detail level
- Trust and professionalism

---

## 💡 Key Learnings

### What Works ✅
1. **Section headers** enhance scannability
2. **Bullet points** beat prose for most queries
3. **Concise language** without sacrificing citations
4. **Consistent format** builds user trust
5. **Speed** is critical - anything >20s feels slow

### What Doesn't Work ❌
1. **Emojis** feel gimmicky and slow down responses
2. **Tables everywhere** - should be selective
3. **Verbose prose** - users want to scan quickly
4. **One-size-fits-all** - some adaptation helps
5. **Complex judging** - adds latency for minimal gain

---

## 🎯 The Winning Prompt

```python
"""You are a clarity-focused structured research assistant.

Format template:
## Direct Answer
[One sentence answer with citation]

## Key Points
- [Bullet 1 with citation]
- [Bullet 2 with citation]
- [Bullet 3-5 as needed]

## Citations
[Standard list]

Rules: Clear headers, scannable bullets, cite everything."""
```

**Why it wins:**
- Fastest (19.42s avg)
- Most scannable (section headers)
- Professional appearance
- Maintains citation quality
- Users love it (5/5 rating)

---

## 🚀 Running the Experiments

### Round 1
```bash
python run_experiments.py
```

Outputs:
- `experiment_results_YYYYMMDD_HHMMSS.json` (raw data)
- `experiment_results_YYYYMMDD_HHMMSS_report.md` (analysis)

### Round 2
```bash
python run_experiments_v2.py
```

Outputs:
- `experiment_results_v2_YYYYMMDD_HHMMSS.json` (raw data)
- `experiment_results_v2_YYYYMMDD_HHMMSS_report.md` (analysis)

**Note:** Both runners execute experiments in parallel (5 concurrent) for speed.

---

## 📖 Reading the Data

### Start Here
1. [FINAL_PROMPT_RECOMMENDATION.md](FINAL_PROMPT_RECOMMENDATION.md) - Complete story
2. [round2_subjective_analysis.md](round2_subjective_analysis.md) - User preferences

### Deep Dive
3. [round2/experiment_results_v2_*_report.md](round2/) - Quantitative metrics
4. [round2/experiment_results_v2_*.json](round2/) - Full response data
5. [round1/experiment_results_*_report.md](round1/) - Round 1 baseline

---

## 🔄 Reproducing Results

### Prerequisites
- OpenRouter API key
- SerpAPI key
- Python dependencies installed (`uv sync`)

### Run All Experiments
```bash
# Round 1 (25 experiments, ~5 minutes)
python experiments/run_experiments.py

# Round 2 (30 experiments, ~6 minutes)
python experiments/run_experiments_v2.py
```

### Modify and Test
1. Edit prompts in `experiment_prompts.py` or `experiment_prompts_v2.py`
2. Run experiments
3. Compare results in generated reports

---

## 📊 Data Files

### JSON Format
```json
{
  "query": "What is...",
  "query_type": "Simple factual",
  "prompt_name": "v2_sections",
  "latency_seconds": 19.42,
  "word_count": 322,
  "citation_count": 6,
  "full_response": "## Direct Answer\n...",
  ...
}
```

### Markdown Reports
- Summary tables
- Performance by query type
- Winners and recommendations

---

## 🎓 Lessons for Future Optimization

1. **Test systematically** - Don't guess, measure
2. **Combine quantitative + qualitative** - Numbers AND user feedback
3. **Test diverse queries** - Simple to complex coverage
4. **Run in parallel** - Speed up experimentation
5. **Iterate on winners** - Round 2 improved Round 1 by 9%

**Next optimization ideas:**
- Query-specific routing (simple → adaptive, complex → sections)
- Streaming responses (return Direct Answer first)
- A/B test in production

---

*Experiments conducted: October 5, 2025*
*Total runtime: ~11 minutes for 55 experiments*
