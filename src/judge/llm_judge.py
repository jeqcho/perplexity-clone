"""LLM Judge that evaluates agent outputs and selects the best response."""

from typing import List, Dict
from src.llm.openai_client import OpenAIClient


class LLMJudge:
    """Judge that evaluates multiple agent responses and selects the best one."""

    def __init__(self, llm_client: OpenAIClient = None):
        """Initialize the LLM judge.

        Args:
            llm_client: OpenAI client instance. If not provided, creates a new one.
        """
        self.llm_client = llm_client or OpenAIClient()

    def evaluate_responses(
        self,
        query: str,
        agent_responses: List[Dict[str, str]]
    ) -> str:
        """Evaluate agent responses and return the best one.

        Args:
            query: The original user query
            agent_responses: List of dicts with 'agent_name' and 'response' keys

        Returns:
            The best response (unchanged from the winning agent)

        Raises:
            Exception: If LLM API call fails or no valid response is found
        """
        if not agent_responses:
            raise ValueError("No agent responses to evaluate")

        # Format responses for evaluation
        responses_text = self._format_responses(agent_responses)

        system_prompt = """You are an expert judge evaluating search result answers. Your task is to select the BEST response based on these criteria:

1. ACCURACY: Information is correct and well-supported by citations
2. CITATION QUALITY: Proper use of numbered citations [1], [2], etc. with complete citation list
3. COHERENCE: Answer is well-structured, clear, and easy to understand
4. COMPLETENESS: Answer thoroughly addresses the user's query
5. RELEVANCE: Information directly pertains to the question asked

You MUST respond with ONLY the number (1, 2, or 3) of the best response. Do not include any explanation or other text."""

        user_prompt = f"""Query: {query}

{responses_text}

Based on the evaluation criteria (accuracy, citation quality, coherence, completeness, relevance), which response is BEST?

Respond with ONLY the number (1, 2, or 3) of the best response."""

        try:
            judgment = self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=50,  # Increased from 10 to give model more room
                temperature=0  # Deterministic selection
            )

            # Handle empty or invalid response - default to first agent
            if not judgment or not judgment.strip():
                print("⚠ Warning: Judge returned empty response, using first agent")
                return agent_responses[0]["response"]

            # Extract number from response
            import re
            numbers = re.findall(r'\d+', judgment.strip())

            if not numbers:
                print("⚠ Warning: Judge did not return a number, using first agent")
                return agent_responses[0]["response"]

            # Parse the judgment
            selected_index = int(numbers[0]) - 1

            if 0 <= selected_index < len(agent_responses):
                return agent_responses[selected_index]["response"]
            else:
                # Default to first agent if out of range
                print(f"⚠ Warning: Judge returned invalid index {numbers[0]}, using first agent")
                return agent_responses[0]["response"]

        except (ValueError, Exception) as e:
            raise Exception(f"Judge evaluation failed: {str(e)}") from e

    def _format_responses(self, agent_responses: List[Dict[str, str]]) -> str:
        """Format agent responses for evaluation.

        Args:
            agent_responses: List of response dictionaries

        Returns:
            Formatted string of all responses
        """
        formatted = []
        for idx, response_data in enumerate(agent_responses, 1):
            agent_name = response_data.get("agent_name", f"Agent {idx}")
            response = response_data.get("response", "")
            formatted.append(
                f"Response {idx} ({agent_name}):\n{response}\n"
                f"{'-' * 80}\n"
            )
        return "\n".join(formatted)
