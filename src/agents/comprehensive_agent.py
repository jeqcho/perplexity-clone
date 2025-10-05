"""Comprehensive agent that focuses on broad coverage of the topic."""

from src.agents.base_agent import BaseAgent


class ComprehensiveAgent(BaseAgent):
    """Agent that prioritizes broad, comprehensive coverage of all aspects."""

    def get_strategy_name(self) -> str:
        """Return the name of this agent's strategy."""
        return "Comprehensive Agent"

    def get_system_prompt(self) -> str:
        """Return the optimized system prompt (v2_sections - Round 2 winner).

        Performance: 19.42s avg latency, 322 words, 6.4 citations
        31% faster than original, 50% more concise, 5/5 user rating
        """
        return """You are a clarity-focused structured research assistant.

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
