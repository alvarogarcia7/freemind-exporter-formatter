from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml
from datetime import datetime, date
from typing import Optional, List, Dict, Any, cast


class Formatter(MindmapExporter):
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
        date_nodes = self._find_all_date_nodes(tree)
        self.result = []

        for date_node in date_nodes:
            date_val = self._get_date_from_node(date_node)
            if not date_val:
                continue

            sections = []
            for child in date_node:
                if child.tag == 'node' and 'TEXT' in child.attrib:
                    section_name = child.get('TEXT')
                    sections.append({
                        'name': section_name,
                        'node': child
                    })

            if sections:
                self.result.append({
                    'date': date_val,
                    'sections': sections
                })

    def format(self) -> list[str]:
        """Format dates and sections into orgmode."""
        if self.result is None:
            return []

        lines = []
        sorted_dates = sorted(self.result, key=lambda x: x['date'])

        for date_entry in sorted_dates:
            date_val = date_entry['date']
            formatted_date = date_val.strftime('%Y-%m-%d %a')
            lines.append(f"* [{formatted_date}]")

            for section in date_entry['sections']:
                self._process_section(section, lines)

            lines.append("")  # Blank line after date

        return lines

    def _process_section(self, section: Dict[str, Any], lines: List[str]) -> None:
        """Route section to appropriate handler."""
        section_name = section['name']
        section_node = section['node']

        # Header line - special case for TODO section
        if section_name == "TODO":
            lines.append("** TODO")
        else:
            lines.append(f"** PROJ {section_name}")

        # Content processing
        if section_name == "TIMES":
            self._process_times_section(section_node, lines)
        else:
            self._process_hierarchical_section(section_node, lines)

        lines.append("")  # Blank line after section

    def _process_times_section(self, section_node: xml.Element, lines: List[str]) -> None:
        """
        Process TIMES section with datetime entries.
        Format: HH:MM - HH:MM: description :tags:
        """
        entries = []

        for child in section_node:
            if child.tag != 'node':
                continue

            if self._is_datetime_node(child):
                start_time = self._parse_datetime_from_node(child)
                if start_time:
                    end_time = self._find_end_time(child)
                    description, tags = self._get_task_description(child)

                    entries.append({
                        'start': start_time,
                        'end': end_time,
                        'description': description,
                        'tags': tags
                    })

        # Auto-fill missing end times
        for i in range(len(entries) - 1):
            if entries[i]['end'] is None:
                entries[i]['end'] = entries[i + 1]['start']

        # Format entries
        for entry in entries:
            entry_start: datetime = cast(datetime, entry['start'])
            entry_end: Optional[datetime] = cast(Optional[datetime], entry['end'])
            entry_tags: List[str] = cast(List[str], entry['tags'])
            entry_desc: str = cast(str, entry['description'])

            start_str = entry_start.strftime('%H:%M')
            end_str = entry_end.strftime('%H:%M') if entry_end else 'noend'

            tags_str = f" :{':'.join(entry_tags)}:" if entry_tags else ""

            desc_clean = entry_desc.strip() if entry_desc else ""
            if desc_clean:
                lines.append(f"- {start_str} - {end_str}: {desc_clean}{tags_str}")
            else:
                lines.append(f"- {start_str} - {end_str}{tags_str}")

    def _process_hierarchical_section(self, section_node: xml.Element, lines: List[str], level: int = 0) -> None:
        """
        Process section hierarchically with 3-phase ordering.
        - Leaf nodes → list items (with indentation)
        - Non-leaf nodes → headers
        - TODO nodes → TODO headers
        """
        children = self._get_node_children(section_node)

        # Phase 1: Leaf items (non-TODO)
        leaf_non_todo = [c for c in children if self._is_leaf(c) and not self._is_todo(c)]
        for child in leaf_non_todo:
            self._format_node_hierarchical(child, lines, level)

        # Phase 2: Non-leaf children (non-TODO)
        nonleaf_non_todo = [c for c in children if not self._is_leaf(c) and not self._is_todo(c)]
        for child in nonleaf_non_todo:
            self._format_node_hierarchical(child, lines, level)

        # Phase 3: TODO children
        todos = [c for c in children if self._is_todo(c)]
        for child in todos:
            self._format_node_hierarchical(child, lines, level)

    def _format_node_hierarchical(self, node: xml.Element, lines: List[str], level: int) -> None:
        """Format a single node hierarchically."""
        text = node.attrib.get('TEXT', '')
        is_todo = self._is_todo(node)
        is_leaf = self._is_leaf(node)

        # Clean TODO marker
        if is_todo:
            text = text.strip()[1:].strip()

        # For non-leaf nodes at level 0, check if all children are leaves
        # If so, format as list items; otherwise, format as headers
        is_simple_node = False
        if not is_leaf and level == 0:
            children = self._get_node_children(node)
            all_children_are_leaves = all(self._is_leaf(c) or self._is_todo(c) for c in children)
            if all_children_are_leaves:
                is_simple_node = True

        # Determine format
        if is_todo:
            # TODO nodes are always headers
            stars = '*' * (level + 3)  # +3 for date and section levels
            lines.append(f"{stars} TODO {text}")
        elif is_leaf:
            # Leaf nodes are list items with indentation
            indent = '  ' * level
            lines.append(f"{indent}- {text}")
        elif is_simple_node:
            # Simple non-leaf nodes (level 0 with only leaf children) are list items
            indent = '  ' * level
            lines.append(f"{indent}- {text}")
        else:
            # Non-leaf nodes are PROJ headers
            stars = '*' * (level + 3)
            lines.append(f"{stars} PROJ {text}")

        # Process children recursively for non-leaf nodes
        if not is_leaf:
            self._process_hierarchical_section(node, lines, level + 1)

    # ========== Date Processing Methods (from orgmode.py) ==========

    def _find_all_date_nodes(self, root: xml.Element) -> List[xml.Element]:
        """Find all date nodes in the tree recursively."""
        date_nodes: List[xml.Element] = []
        self._find_date_nodes_recursive(root, date_nodes)
        return date_nodes

    def _find_date_nodes_recursive(self, node: xml.Element, date_nodes: List[xml.Element]) -> None:
        """Recursively search for date nodes."""
        obj_attr = node.get('OBJECT', '')
        if 'FormattedDate' in obj_attr and obj_attr.endswith('|date'):
            date_nodes.append(node)

        for child in node:
            if child.tag == 'node':
                self._find_date_nodes_recursive(child, date_nodes)

    def _get_date_from_node(self, node: xml.Element) -> Optional[date]:
        """Extract date from node's OBJECT attribute."""
        obj_attr = node.get('OBJECT', '')
        if 'FormattedDate' in obj_attr:
            parts = obj_attr.split('|')
            if len(parts) >= 2:
                date_str = parts[1]
                try:
                    dt = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
                    return dt.date()
                except ValueError:
                    pass
        return None

    # ========== DateTime Processing Methods (from orgmode.py) ==========

    def _is_datetime_node(self, node: xml.Element) -> bool:
        """Check if node contains datetime information."""
        obj_attr = node.get('OBJECT', '')
        return 'FormattedDate' in obj_attr and 'datetime' in obj_attr

    def _parse_datetime_from_node(self, node: xml.Element) -> Optional[datetime]:
        """Parse datetime from node's OBJECT attribute."""
        obj_attr = node.get('OBJECT', '')
        if 'FormattedDate' in obj_attr and 'datetime' in obj_attr:
            parts = obj_attr.split('|')
            if len(parts) >= 2:
                datetime_str = parts[1]
                try:
                    if 'T' in datetime_str:
                        if '+' in datetime_str:
                            dt_part = datetime_str.split('+')[0]
                        else:
                            dt_parts = datetime_str.split('-')
                            if len(dt_parts) >= 3:
                                dt_part = f"{dt_parts[0]}-{dt_parts[1]}-{dt_parts[2]}"
                            else:
                                dt_part = datetime_str
                        return datetime.strptime(dt_part, '%Y-%m-%dT%H:%M')
                except ValueError:
                    pass
        return None

    def _find_end_time(self, start_node: xml.Element) -> Optional[datetime]:
        """Find end time in children of a datetime node."""
        for child in start_node:
            if child.tag == 'node':
                end_time = self._parse_datetime_from_node(child)
                if end_time:
                    return end_time
        return None

    def _get_task_description(self, time_node: xml.Element) -> tuple[str, list[str]]:
        """Extract task description and tags from a datetime node."""
        children = list(time_node)
        tags: List[str] = []
        description = ""

        # First pass: extract icon tags
        for child in children:
            if child.tag == 'icon':
                tags.append("".join(list(map(lambda x: x.title(), child.attrib['BUILTIN'].split("-")))))

        # Second pass: find description and text-based tags
        for child in children:
            if child.tag == 'node':
                child_time = self._parse_datetime_from_node(child)
                # Skip datetime children (end times)
                if not child_time:
                    text = child.get('TEXT', '').strip()
                    if text:
                        # If this node has children, recurse to find actual description
                        grandchildren = self._get_node_children(child)
                        if grandchildren:
                            # This node might be a tag wrapper, check its children
                            found_description = False
                            for grandchild in grandchildren:
                                if not self._is_datetime_node(grandchild):
                                    grandtext = grandchild.get('TEXT', '').strip()
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

    def _extract_tags_from_node(self, node: xml.Element) -> List[str]:
        """Extract icon tags from a node and convert to TitleCase."""
        tags: List[str] = []
        for child in node:
            if child.tag == 'icon':
                builtin = child.attrib.get('BUILTIN', '')
                if builtin:
                    parts = builtin.split("-")
                    tags.append("".join([p.title() for p in parts]))
        return tags

    # ========== Hierarchical Processing Methods (from orgmode_lists.py) ==========

    def _is_leaf(self, node: xml.Element) -> bool:
        """Returns True if node has no node children."""
        return len(self._get_node_children(node)) == 0

    def _is_todo(self, node: xml.Element) -> bool:
        """Returns True if node text starts with '!'."""
        text = node.attrib.get('TEXT', '').strip()
        return text.startswith('!')

    def _get_node_children(self, node: xml.Element) -> List[xml.Element]:
        """Returns list of node children (filters to only 'node' tags)."""
        return [child for child in node if child.tag == 'node']
