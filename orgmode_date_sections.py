from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml
from datetime import datetime, date
from typing import Optional, List, Any
from html.parser import HTMLParser
from mindmap.reader import DateReader, DateTimeReader, NodeTreeHelper
from mindmap.models import DateTimeValue, TimeEntry, Section, DateEntry
from worklog.format import TodoHelper


class Formatter(MindmapExporter, NodeTreeHelper):
    """
    Exports date nodes and their child sections (WORKLOG, TIMES, TODO, etc.)
    in orgmode format.

    Key Features:
    - Finds all date nodes in the mindmap
    - Processes ALL child sections (not filtered by name)
    - TIMES section: formatted with timestamps and durations
    - Other sections: formatted hierarchically (leaf/non-leaf/TODO)
    - Special handling for TODO section name (no PROJ prefix)
    """

    def parse(self, tree: xml.Element) -> None:
        """Find all date nodes and extract sections."""
        date_nodes = DateReader.find_all_date_nodes(tree)
        self.result: List[DateEntry] = []

        for date_node in date_nodes:
            date_val = DateReader.read_date(date_node)
            if not date_val:
                continue

            sections: List[Section] = []
            for child in date_node:
                if child.tag == "node" and "TEXT" in child.attrib:
                    section_name = child.get("TEXT", "")
                    sections.append(Section(name=section_name, node=child))

            if sections:
                self.result.append(DateEntry(date=date_val, sections=sections))

    def format(self) -> list[str]:
        """Format dates and sections into orgmode."""
        lines = []
        sorted_dates = sorted(self.result, key=lambda x: x.sort_key())

        for date_entry in sorted_dates:
            lines.append(f"* {date_entry.date.format_header()}")

            for idx, section in enumerate(date_entry.sections):
                is_last = idx == len(date_entry.sections) - 1
                self._process_section(section, lines, is_last=is_last)

        return lines

    def _process_section(
        self, section: Section, lines: List[str], is_last: bool = False
    ) -> None:
        """Route section to appropriate handler."""
        section_name = section.name
        section_node = section.node

        # Header line - special case for TODO section
        if section.is_todo_section():
            lines.append("** TODO")
        else:
            lines.append(f"** PROJ {section_name}")

        # Content processing
        if section.is_times_section():
            self._process_times_section(section_node, lines)
        elif section.is_todo_section():
            # TODO section: all nodes become headers
            self._process_todo_section(section_node, lines)
        else:
            # Pass section_name to hierarchical processing
            self._process_hierarchical_section(
                section_node, lines, section_name=section_name
            )

        # Add blank line after each section
        # Two blank lines after WORKLOG, one blank line after others
        if not is_last:
            if section_name == "WORKLOG":
                lines.append("")  # First blank line
                lines.append("")  # Second blank line
            else:
                lines.append("")  # Single blank line

    def _process_times_section(
        self, section_node: xml.Element, lines: List[str]
    ) -> None:
        """
        Process TIMES section with datetime entries.
        Format: HH:MM - HH:MM: description :tags:
        """
        entries: List[TimeEntry] = []

        for child in section_node:
            if child.tag != "node":
                continue

            if DateTimeReader.is_datetime_node(child):
                start_time = DateTimeReader.read_datetime(child)
                if start_time:
                    end_time = self._find_end_time_internal(child)
                    description, tags = self._get_task_description(child)

                    entries.append(
                        TimeEntry(
                            start=start_time,
                            end=end_time,
                            description=description,
                            tags=tags,
                        )
                    )

        # Auto-fill missing end times
        for i in range(len(entries) - 1):
            if entries[i].end is None:
                entries[i] = TimeEntry(
                    start=entries[i].start,
                    end=entries[i + 1].start,
                    description=entries[i].description,
                    tags=entries[i].tags,
                )

        # Format entries (skip "End" entries)
        for entry in entries:
            desc_clean = entry.description.strip() if entry.description else ""

            # Skip "End" entries
            if desc_clean.lower() == "end":
                continue

            lines.append(entry.format_line())

    def _process_todo_section(
        self, section_node: xml.Element, lines: List[str], level: int = 0
    ) -> None:
        """
        Process TODO section where all nodes become headers regardless of leaf status.
        Also extracts richcontent (HTML notes) and renders as list items.
        """
        children = NodeTreeHelper.get_node_children(section_node)

        for child in children:
            self._format_todo_node(child, lines, level)

    def _format_todo_node(
        self, node: xml.Element, lines: List[str], level: int
    ) -> None:
        """Format a node in TODO section as a header."""
        text = node.attrib.get("TEXT", "")
        is_todo_marked = TodoHelper.is_todo(node)

        # Clean TODO marker if present
        if is_todo_marked:
            text = TodoHelper.clean_todo_text(text)

        # In TODO section: all items become TODO by default
        # unless marked with ! for explicit PROJ
        stars = "*" * (level + 3)

        if level == 0:
            # Top-level items in TODO section
            is_leaf = NodeTreeHelper.is_leaf(node)
            if is_leaf:
                # Leaf items become TODO headers
                lines.append(f"{stars} TODO {text}")
            else:
                # Non-leaf items become PROJ headers
                lines.append(f"{stars} PROJ {text}")
        else:
            # Nested items are TODO by default
            lines.append(f"{stars} TODO {text}")

        # Extract and process richcontent (HTML notes) BEFORE children
        self._extract_and_render_richcontent(node, lines, level)

        # Process children recursively
        children = NodeTreeHelper.get_node_children(node)
        for child in children:
            self._format_todo_node(child, lines, level + 1)

    def _extract_and_render_richcontent(
        self, node: xml.Element, lines: List[str], level: int
    ) -> None:
        """Extract richcontent HTML and render as list items."""
        for child in node:
            if child.tag == "richcontent":
                content_type = child.attrib.get("TYPE", "")
                if content_type == "NOTE":
                    # Find the HTML content
                    html_elem = child.find("html")
                    if html_elem is not None:
                        html_text = xml.tostring(html_elem, encoding="unicode")
                        # Parse HTML and extract list items
                        list_items = self._parse_html_list(html_text)

                        # Check if any item has indentation - if so, indent all items uniformly
                        has_indented_item = any(
                            item.startswith("  ") for item in list_items
                        )

                        # Richcontent is always rendered at level 0
                        for idx, item in enumerate(list_items):
                            stripped = item.lstrip(" ")
                            indent = item[: len(item) - len(stripped)]

                            if has_indented_item:
                                # If there are nested items, indent all items uniformly
                                if idx == 0:
                                    # First item (usually the parent of any nested items)
                                    lines.append(f"- {stripped}")
                                else:
                                    # All other items are indented
                                    lines.append(f"  - {stripped}")
                            else:
                                # No indentation pattern - render as-is
                                if indent:
                                    lines.append(f"{indent}- {stripped}")
                                else:
                                    lines.append(f"- {stripped}")
                        # Only process the first richcontent NOTE
                        break

    def _parse_html_list(self, html_text: str) -> List[str]:
        """Parse HTML and extract list item texts recursively, maintaining nesting."""

        class HTMLListParser(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.root: List[dict[str, Any]] = []  # Root level items
                self.li_stack: List[dict[str, Any]] = []  # Stack of open list items
                self.ul_depth = 0  # Current nesting depth

            def handle_starttag(
                self, tag: str, attrs: List[tuple[str, Optional[str]]]
            ) -> None:
                if tag == "ul":
                    self.ul_depth += 1
                elif tag == "li":
                    # Start of a new list item
                    new_item = {"text": "", "depth": self.ul_depth, "children": []}
                    # Add to parent's children or to root
                    if self.li_stack and self.li_stack[-1]["depth"] < self.ul_depth:
                        self.li_stack[-1]["children"].append(new_item)
                    else:
                        self.root.append(new_item)
                    self.li_stack.append(new_item)

            def handle_endtag(self, tag: str) -> None:
                if tag == "ul":
                    self.ul_depth -= 1
                elif tag == "li":
                    # End of list item
                    if self.li_stack:
                        item = self.li_stack.pop()
                        item["text"] = item["text"].strip()

            def handle_data(self, data: str) -> None:
                # Add text to the current item
                if self.li_stack:
                    self.li_stack[-1]["text"] += data

        parser = HTMLListParser()
        try:
            parser.feed(html_text)
        except Exception:
            # If parsing fails, return empty list
            pass

        # Convert tree to flat list, returning items with depth info
        def flatten_tree(
            items: List[dict[str, Any]], depth: int = 0
        ) -> List[tuple[int, str]]:
            result = []
            for item in items:
                if item["text"]:
                    result.append((depth, item["text"]))
                # Add children
                if item["children"]:
                    result.extend(flatten_tree(item["children"], depth + 1))
            return result

        # Convert to final format (indentation in output)
        flat_items = flatten_tree(parser.root)
        result = []
        for depth, text in flat_items:
            indent = "  " * depth
            result.append(f"{indent}{text}" if depth > 0 else text)
        return result

    def _process_hierarchical_section(
        self,
        section_node: xml.Element,
        lines: List[str],
        level: int = 0,
        section_name: str = "",
    ) -> None:
        """
        Process section hierarchically with 3-phase ordering.
        - Leaf nodes → list items (with indentation)
        - Non-leaf nodes → headers
        - TODO nodes → TODO headers
        """
        children = NodeTreeHelper.get_node_children(section_node)

        # Phase 1: Leaf items (non-TODO)
        leaf_non_todo = [
            c
            for c in children
            if NodeTreeHelper.is_leaf(c) and not TodoHelper.is_todo(c)
        ]
        for child in leaf_non_todo:
            self._format_node_hierarchical(
                child, lines, level, section_name=section_name
            )

        # Phase 2: Non-leaf children (non-TODO)
        nonleaf_non_todo = [
            c
            for c in children
            if not NodeTreeHelper.is_leaf(c) and not TodoHelper.is_todo(c)
        ]
        for child in nonleaf_non_todo:
            self._format_node_hierarchical(
                child, lines, level, section_name=section_name
            )

        # Phase 3: TODO children
        todos = [c for c in children if TodoHelper.is_todo(c)]
        for child in todos:
            self._format_node_hierarchical(
                child, lines, level, section_name=section_name
            )

    def _format_node_hierarchical(
        self, node: xml.Element, lines: List[str], level: int, section_name: str = ""
    ) -> None:
        """Format a single node hierarchically."""
        text = node.attrib.get("TEXT", "")
        is_todo = TodoHelper.is_todo(node)
        is_leaf = NodeTreeHelper.is_leaf(node)

        # Clean TODO marker
        if is_todo:
            text = TodoHelper.clean_todo_text(text)

        # For non-leaf nodes at level 0 in WORKLOG or LEARNLOG, check if all children are leaves
        # If so, format as list items; otherwise, format as headers
        is_simple_node = False
        if not is_leaf and level == 0 and section_name in ("WORKLOG", "LEARNLOG"):
            children = NodeTreeHelper.get_node_children(node)
            all_children_are_leaves = all(
                NodeTreeHelper.is_leaf(c) or TodoHelper.is_todo(c) for c in children
            )
            if all_children_are_leaves:
                is_simple_node = True

        # Determine format
        if is_todo:
            # TODO nodes are always headers
            stars = "*" * (level + 3)  # +3 for date and section levels
            lines.append(f"{stars} TODO {text}")
        elif is_leaf:
            # Leaf nodes are list items with indentation
            indent = "  " * level
            lines.append(f"{indent}- {text}")
        elif is_simple_node:
            # Simple non-leaf nodes (level 0 with only leaf children) are list items
            indent = "  " * level
            lines.append(f"{indent}- {text}")
        else:
            # Non-leaf nodes are headers
            stars = "*" * (level + 3)
            # Add PROJ prefix for most sections, but not for RAYW
            if section_name == "RAYW":
                lines.append(f"{stars} {text}")
            else:
                lines.append(f"{stars} PROJ {text}")

        # Process children recursively for non-leaf nodes
        if not is_leaf:
            # If this node became a header (not a list item), keep the same level for children
            # Otherwise, increment level for indentation
            next_level = level if not is_simple_node else level + 1
            self._process_hierarchical_section(
                node, lines, next_level, section_name=section_name
            )

    def _find_end_time_internal(
        self, start_node: xml.Element
    ) -> Optional[DateTimeValue]:
        """Find end time in children of a datetime node (returns DateTimeValue)."""
        for child in start_node:
            if child.tag == "node":
                end_time = DateTimeReader.read_datetime(child)
                if end_time:
                    return end_time
        return None

    def _find_end_time(self, start_node: xml.Element) -> Optional[datetime]:
        """Find end time in children of a datetime node (returns raw datetime for backward compatibility)."""
        end_time_val = self._find_end_time_internal(start_node)
        return end_time_val.value if end_time_val else None

    # ========== Backward-compatible methods (delegate to value object classes) ==========

    def _find_all_date_nodes(self, root: xml.Element) -> List[xml.Element]:
        """Find all date nodes in the tree recursively."""
        return DateReader.find_all_date_nodes(root)

    def _get_date_from_node(self, node: xml.Element) -> Optional[date]:
        """Extract date from node's OBJECT attribute."""
        date_val = DateReader.read_date(node)
        return date_val.value if date_val else None

    def _is_datetime_node(self, node: xml.Element) -> bool:
        """Check if node contains datetime information."""
        return DateTimeReader.is_datetime_node(node)

    def _parse_datetime_from_node(self, node: xml.Element) -> Optional[datetime]:
        """Parse datetime from node's OBJECT attribute."""
        dt_val = DateTimeReader.read_datetime(node)
        return dt_val.value if dt_val else None

    def _get_task_description(self, time_node: xml.Element) -> tuple[str, list[str]]:
        """Extract task description and tags from a datetime node."""
        children = list(time_node)
        tags: List[str] = []
        description = ""

        # First pass: extract icon tags
        for child in children:
            if child.tag == "icon":
                tags.append(
                    "".join(
                        list(
                            map(lambda x: x.title(), child.attrib["BUILTIN"].split("-"))
                        )
                    )
                )

        # Second pass: find description and text-based tags
        for child in children:
            if child.tag == "node":
                child_time = DateTimeReader.read_datetime(child)
                # Skip datetime children (end times)
                if not child_time:
                    text = child.get("TEXT", "").strip()
                    if text:
                        # If this node has children, recurse to find actual description
                        grandchildren = NodeTreeHelper.get_node_children(child)
                        if grandchildren:
                            # This node might be a tag wrapper, check its children
                            found_description = False
                            for grandchild in grandchildren:
                                if not DateTimeReader.is_datetime_node(grandchild):
                                    grandtext = grandchild.get("TEXT", "").strip()
                                    if grandtext and not found_description:
                                        description = grandtext
                                        found_description = True
                                        # Treat the intermediate node text as a tag
                                        if text and text not in tags:
                                            tags.append(text)
                                        break
                        else:
                            # No children, use this text as description
                            if not description:
                                description = text

        return description, tags

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

    def _extract_tags_from_node(self, node: xml.Element) -> List[str]:
        """Backward-compatible wrapper for NodeTreeHelper.extract_tags_from_node()."""
        return NodeTreeHelper.extract_tags_from_node(node)
