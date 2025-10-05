"""Utilities for validating agent responses."""

from typing import Dict, List
from src.utils.citation_formatter import CitationFormatter


class ResponseValidator:
    """Validates agent responses for consistency and quality."""

    @staticmethod
    def validate_agent_response(response: str, agent_name: str) -> Dict[str, any]:
        """Validate a single agent response.

        Args:
            response: The agent's response text
            agent_name: Name of the agent for error reporting

        Returns:
            Dict with 'valid' (bool), 'issues' (list), and 'response' (str) keys
        """
        issues = []

        # Check if response is empty
        if not response or not response.strip():
            issues.append(f"{agent_name}: Empty response")
            return {"valid": False, "issues": issues, "response": response}

        # Validate citation format
        is_valid, citation_issues = CitationFormatter.validate_citations(response)
        if not is_valid:
            issues.extend([f"{agent_name}: {issue}" for issue in citation_issues])

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "response": response
        }

    @staticmethod
    def validate_all_responses(
        agent_responses: List[Dict[str, str]]
    ) -> Dict[str, any]:
        """Validate all agent responses.

        Args:
            agent_responses: List of dicts with 'agent_name' and 'response' keys

        Returns:
            Dict with 'valid' (bool), 'issues' (list), and 'responses' (list) keys
        """
        all_issues = []
        validated_responses = []

        for response_data in agent_responses:
            agent_name = response_data.get("agent_name", "Unknown Agent")
            response = response_data.get("response", "")

            validation = ResponseValidator.validate_agent_response(response, agent_name)
            all_issues.extend(validation["issues"])
            validated_responses.append(response_data)

        return {
            "valid": len(all_issues) == 0,
            "issues": all_issues,
            "responses": validated_responses
        }
