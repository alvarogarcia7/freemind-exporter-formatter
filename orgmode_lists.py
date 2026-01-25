from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml
from typing import List


class Formatter(MindmapExporter):
    def parse(self, tree: xml.Element) -> None:
        """Parse the XML tree and collect lines."""
        self.lines = ["#+title: Export", ""]
        self._parse_node(tree, 1)

    def format(self) -> list[str]:
        """Return the formatted lines (already populated during parse)."""
        return self.lines.copy()

    def _parse_node(self, node: xml.Element, level: int) -> None:
        # Skip elements that don't have TEXT attribute (e.g., font, hook, edge elements)
        if "TEXT" not in node.attrib:
            # Still process children of non-TEXT elements
            for child in node:
                self._parse_node(child, level)
            return

        text = node.attrib["TEXT"]
        is_todo = self._is_todo(node)
        is_leaf = self._is_leaf(node)

        # Clean up TODO marker from text if needed
        if is_todo:
            text = text.strip()[1:].strip()

        # Determine what to add to lines
        if level == 1:
            # Root node is always PROJ
            self.lines.append(f"* PROJ {node.attrib['TEXT']}")
        elif is_todo:
            # TODO nodes are always headings
            stars = "*" * level
            self.lines.append(f"{stars} TODO {text}")
        elif is_leaf:
            # Leaf nodes (non-TODO) become list items
            self.lines.append(f"- {text}")
        else:
            # Non-leaf nodes (non-TODO) become PROJ headings
            stars = "*" * level
            self.lines.append(f"{stars} PROJ {text}")

        # Process children in three phases
        children = self._get_node_children(node)

        # Phase 1: leaf items (non-TODO)
        leaf_non_todo = [
            c for c in children if self._is_leaf(c) and not self._is_todo(c)
        ]
        for child in leaf_non_todo:
            self._parse_node(child, level + 1)

        # Phase 2: non-leaf children (non-TODO)
        nonleaf_non_todo = [
            c for c in children if not self._is_leaf(c) and not self._is_todo(c)
        ]
        for child in nonleaf_non_todo:
            self._parse_node(child, level + 1)

        # Phase 3: TODO children (leaf or non-leaf)
        todos = [c for c in children if self._is_todo(c)]
        for child in todos:
            self._parse_node(child, level + 1)

    def _is_leaf(self, node: xml.Element) -> bool:
        """Returns True if node has no node children."""
        return len(self._get_node_children(node)) == 0

    def _is_todo(self, node: xml.Element) -> bool:
        """Returns True if node text starts with '!'."""
        text = node.attrib.get("TEXT", "").strip()
        return text.startswith("!")

    def _get_node_children(self, node: xml.Element) -> List[xml.Element]:
        """Returns list of node children (filters to only 'node' tags)."""
        return [child for child in node if child.tag == "node"]
