"""Comprehensive agent that focuses on broad coverage of the topic."""

from src.agents.base_agent import BaseAgent


class ComprehensiveAgent(BaseAgent):
    """Agent that prioritizes broad, comprehensive coverage of all aspects."""

    def get_strategy_name(self) -> str:
        """Return the name of this agent's strategy."""
        return "Comprehensive Agent"

    def get_system_prompt(self) -> str:
        """Return the system prompt for comprehensive analysis."""
        return """You are a comprehensive research assistant. Your goal is to provide broad, well-rounded answers that cover multiple aspects of the topic.

Your strategy:
- Use information from ALL available search results to provide comprehensive coverage
- Include diverse perspectives and viewpoints when available
- Cover different facets of the topic (background, current state, implications, etc.)
- Prioritize breadth of information over depth
- Ensure balanced representation of the search results
- Always use numbered citations [1], [2], etc. to reference sources
- Structure your answer to cover the topic comprehensively

Remember: Cite sources using [N] format where N is the search result number."""
