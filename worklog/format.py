"""TODO formatting and handling utilities."""

from __future__ import annotations

import xml.etree.ElementTree as xml


class TodoHelper:
    """Helper class for TODO detection and text processing."""

    @staticmethod
    def is_todo(node: xml.Element) -> bool:
        """Check if node text starts with '!' (TODO marker)."""
        text = node.attrib.get("TEXT", "").strip()
        return text.startswith("!")

    @staticmethod
    def clean_todo_text(text: str) -> str:
        """Remove TODO marker ('!') from beginning of text."""
        if text.strip().startswith("!"):
            return text.strip()[1:].strip()
        return text
