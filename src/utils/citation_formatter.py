"""Utilities for formatting and validating numbered citations."""

import re
from typing import List, Tuple


class CitationFormatter:
    """Handles citation formatting and validation."""

    @staticmethod
    def validate_citations(text: str) -> Tuple[bool, List[str]]:
        """Validate that text contains properly formatted numbered citations.

        Args:
            text: Text to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check for citation pattern [N]
        citation_pattern = r'\[(\d+)\]'
        citations = re.findall(citation_pattern, text)

        if not citations:
            issues.append("No citations found in the text")
            return False, issues

        # Check for citation list at the end
        citation_list_pattern = r'Citations?:\s*\n(?:\[\d+\][^\n]+\n?)+'
        if not re.search(citation_list_pattern, text, re.IGNORECASE):
            issues.append("Missing citation list at the end")
            return False, issues

        # Extract citation numbers used in text
        text_citations = set(int(c) for c in citations)

        # Extract citations from the list
        citation_list_match = re.search(
            r'Citations?:\s*\n((?:\[\d+\][^\n]+\n?)+)',
            text,
            re.IGNORECASE
        )

        if citation_list_match:
            list_text = citation_list_match.group(1)
            list_citations = set(int(c) for c in re.findall(r'\[(\d+)\]', list_text))

            # Verify all text citations are in the list
            missing_in_list = text_citations - list_citations
            if missing_in_list:
                issues.append(f"Citations used in text but missing from list: {sorted(missing_in_list)}")

            # Verify all list citations are used in text
            unused_citations = list_citations - text_citations
            if unused_citations:
                issues.append(f"Citations in list but not used in text: {sorted(unused_citations)}")

        return len(issues) == 0, issues

    @staticmethod
    def extract_citations(text: str) -> List[str]:
        """Extract citation list from text.

        Args:
            text: Text containing citations

        Returns:
            List of citation strings
        """
        citation_list_match = re.search(
            r'Citations?:\s*\n((?:\[\d+\][^\n]+\n?)+)',
            text,
            re.IGNORECASE
        )

        if citation_list_match:
            list_text = citation_list_match.group(1)
            citations = re.findall(r'(\[\d+\][^\n]+)', list_text)
            return citations

        return []

    @staticmethod
    def format_citation_entry(index: int, title: str, url: str) -> str:
        """Format a single citation entry.

        Args:
            index: Citation number
            title: Source title
            url: Source URL

        Returns:
            Formatted citation string
        """
        return f"[{index}] {title} - {url}"
