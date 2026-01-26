"""Reader classes for mindmap XML parsing and tree traversal."""

from __future__ import annotations

import xml.etree.ElementTree as xml
from typing import List, Optional
from datetime import datetime

from mindmap.models import DateValue, DateTimeValue


class NodeTreeHelper:
    """Provides common node tree traversal and classification utilities."""

    @staticmethod
    def is_leaf(node: xml.Element) -> bool:
        """Check if node has no node children."""
        return len(NodeTreeHelper.get_node_children(node)) == 0

    @staticmethod
    def get_node_children(node: xml.Element) -> List[xml.Element]:
        """Return list of node children (filters to only 'node' tags)."""
        return [child for child in node if child.tag == "node"]

    @staticmethod
    def extract_tags_from_node(node: xml.Element) -> List[str]:
        """Extract icon tags from a node and convert BUILTIN names to TitleCase.

        Example: BUILTIN="stop-sign" -> "StopSign"
        Returns an empty list if no icons present.
        """
        tags: List[str] = []
        for child in node:
            if child.tag == "icon":
                builtin = child.attrib.get("BUILTIN", "")
                if builtin:
                    parts = builtin.split("-")
                    tags.append("".join([p.title() for p in parts]))
        return tags


class DateReader:
    """Reads and parses dates from mindmap XML nodes."""

    @staticmethod
    def find_all_date_nodes(root: xml.Element) -> List[xml.Element]:
        """Find all date nodes in the tree recursively."""
        date_nodes: List[xml.Element] = []
        DateReader._find_date_nodes_recursive(root, date_nodes)
        return date_nodes

    @staticmethod
    def _find_date_nodes_recursive(
        node: xml.Element, date_nodes: List[xml.Element]
    ) -> None:
        """Recursively search for date nodes (matches both |date and |datetime)."""
        obj_attr = node.get("OBJECT", "")
        if "FormattedDate" in obj_attr and "|date" in obj_attr:
            date_nodes.append(node)

        for child in node:
            if child.tag == "node":
                DateReader._find_date_nodes_recursive(child, date_nodes)

    @staticmethod
    def read_date(node: xml.Element) -> Optional[DateValue]:
        """Extract date from node's OBJECT attribute."""
        obj_attr = node.get("OBJECT", "")
        if "FormattedDate" in obj_attr:
            parts = obj_attr.split("|")
            if len(parts) >= 2:
                date_str = parts[1]
                try:
                    dt = datetime.strptime(date_str.split("T")[0], "%Y-%m-%d")
                    return DateValue(dt.date())
                except ValueError:
                    pass
        return None


class DateTimeReader:
    """Reads and parses datetimes from mindmap XML nodes."""

    @staticmethod
    def is_datetime_node(node: xml.Element) -> bool:
        """Check if node contains datetime information."""
        obj_attr = node.get("OBJECT", "")
        return "FormattedDate" in obj_attr and "datetime" in obj_attr

    @staticmethod
    def read_datetime(node: xml.Element) -> Optional[DateTimeValue]:
        """Parse datetime from node's OBJECT attribute."""
        obj_attr = node.get("OBJECT", "")
        if "FormattedDate" in obj_attr and "datetime" in obj_attr:
            parts = obj_attr.split("|")
            if len(parts) >= 2:
                datetime_str = parts[1]
                try:
                    if "T" in datetime_str:
                        if "+" in datetime_str:
                            dt_part = datetime_str.split("+")[0]
                        else:
                            dt_parts = datetime_str.split("-")
                            if len(dt_parts) >= 3:
                                dt_part = f"{dt_parts[0]}-{dt_parts[1]}-{dt_parts[2]}"
                            else:
                                dt_part = datetime_str
                        dt = datetime.strptime(dt_part, "%Y-%m-%dT%H:%M")
                        return DateTimeValue(dt)
                except ValueError:
                    pass
        return None
