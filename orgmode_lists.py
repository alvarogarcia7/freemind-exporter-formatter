from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml
from typing import List
from mindmap.reader import NodeTreeHelper
from worklog.format import TodoHelper


class Formatter(MindmapExporter, NodeTreeHelper):
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
        is_todo = TodoHelper.is_todo(node)
        is_leaf = NodeTreeHelper.is_leaf(node)

        # Clean up TODO marker from text if needed
        if is_todo:
            text = TodoHelper.clean_todo_text(text)

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
        children = NodeTreeHelper.get_node_children(node)

        # Phase 1: leaf items (non-TODO)
        leaf_non_todo = [
            c
            for c in children
            if NodeTreeHelper.is_leaf(c) and not TodoHelper.is_todo(c)
        ]
        for child in leaf_non_todo:
            self._parse_node(child, level + 1)

        # Phase 2: non-leaf children (non-TODO)
        nonleaf_non_todo = [
            c
            for c in children
            if not NodeTreeHelper.is_leaf(c) and not TodoHelper.is_todo(c)
        ]
        for child in nonleaf_non_todo:
            self._parse_node(child, level + 1)

        # Phase 3: TODO children (leaf or non-leaf)
        todos = [c for c in children if TodoHelper.is_todo(c)]
        for child in todos:
            self._parse_node(child, level + 1)

    # ========== Backward-compatible wrapper methods (delegate to NodeTreeHelper) ==========

    def _is_leaf(self, node: xml.Element) -> bool:
        """Backward-compatible wrapper for NodeTreeHelper.is_leaf()."""
        return NodeTreeHelper.is_leaf(node)

    def _is_todo(self, node: xml.Element) -> bool:
        """Backward-compatible wrapper for TodoHelper.is_todo()."""
        return TodoHelper.is_todo(node)

    def _get_node_children(self, node: xml.Element) -> List[xml.Element]:
        """Backward-compatible wrapper for NodeTreeHelper.get_node_children()."""
        return NodeTreeHelper.get_node_children(node)
