"""Worklog formatting helpers and utilities."""

from __future__ import annotations

import xml.etree.ElementTree as xml
from typing import List, Optional, Callable, Tuple, Any, Dict
from datetime import datetime

from mindmap.reader import DateTimeReader, NodeTreeHelper
from worklog.format import TodoHelper


class DateTimeHelper:
    """Helper class for datetime and time entry operations."""

    @staticmethod
    def find_end_time(start_node: xml.Element) -> Optional[datetime]:
        """Find end time in children of a datetime node.

        Searches for a child node with datetime information and extracts
        its datetime value. Returns None if no end time found.
        """
        for child in start_node:
            if child.tag == "node":
                end_time_val = DateTimeReader.read_datetime(child)
                if end_time_val:
                    return end_time_val.value
        return None

    @staticmethod
    def extract_comments(node: xml.Element) -> List[str]:
        """Extract comment text from node children, skipping datetime nodes."""
        comments: List[str] = []
        for child in node:
            if child.tag == "node":
                dt = DateTimeReader.read_datetime(child)
                if not dt:
                    text = child.get("TEXT", "")
                    if text:
                        comments.append(text)
                else:
                    for grandchild in child:
                        if grandchild.tag == "node":
                            text = grandchild.get("TEXT", "")
                            if text:
                                comments.append(text)
        return comments


class DurationFormatter:
    """Utility for formatting time durations."""

    @staticmethod
    def calculate_duration_minutes(entry: Dict[str, Any]) -> int:
        """Calculate duration in minutes from start and end datetime."""
        if entry.get("end") is None:
            return 0
        delta = entry["end"] - entry["start"]
        return int(delta.total_seconds() / 60)

    @staticmethod
    def format_duration(total_minutes: int) -> str:
        """Format duration in minutes as human-readable string.

        Examples: 90 -> "1h 30m", 60 -> "1h", 30 -> "30m", 0 -> "0m"
        """
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return "0m"

    @staticmethod
    def format_time_str(dt: datetime) -> str:
        """Format datetime as HH:MM string."""
        return dt.strftime("%H:%M")

    @staticmethod
    def format_time_entry(entry: Dict[str, Any]) -> str:
        """Format a time entry as 'HH:MM - HH:MM' with optional comments."""
        start_str = DurationFormatter.format_time_str(entry["start"])
        if entry.get("end"):
            end_str = DurationFormatter.format_time_str(entry["end"])
            result = f"{start_str} - {end_str}"
        else:
            result = f"{start_str} -"

        if entry.get("comments"):
            for comment in entry["comments"]:
                result += f" ; {comment}"

        return result

    @staticmethod
    def format_worklog_entry(entry: Dict[str, Any]) -> str:
        """Format a worklog entry as 'HH:MM - HH:MM: task_name'."""
        start_str = DurationFormatter.format_time_str(entry["start"])
        if entry.get("end"):
            end_str = DurationFormatter.format_time_str(entry["end"])
            result = f"{start_str} - {end_str}: {entry['task_name']}"
        else:
            task_name = entry.get("task_name", "")
            if task_name:
                result = f"{start_str} - noend: {task_name}"
            else:
                result = f"{start_str} - noend:"

        return result


class HierarchicalNodeProcessor:
    """Mixin for processing nodes in hierarchical 3-phase order."""

    @staticmethod
    def process_hierarchical_phase(
        nodes: List[xml.Element],
        is_leaf_filter: bool,
        is_todo_filter: bool,
        callback: Callable[..., None],
        callback_args: Tuple[Any, ...],
    ) -> None:
        """Process nodes matching the given filter criteria.

        Args:
            nodes: List of nodes to process
            is_leaf_filter: If True, keep leaf nodes; if False, keep non-leaf
            is_todo_filter: If True, keep TODO nodes; if False, keep non-TODO
            callback: Function to call for each matching node
            callback_args: Extra arguments to pass to callback after (node,)
        """
        matching_nodes = [
            n
            for n in nodes
            if NodeTreeHelper.is_leaf(n) == is_leaf_filter
            and TodoHelper.is_todo(n) == is_todo_filter
        ]

        for node in matching_nodes:
            callback(node, *callback_args)

    @staticmethod
    def filter_and_process(
        nodes: List[xml.Element],
        is_todo_filter: bool,
        callback: Callable[..., None],
        callback_args: Tuple[Any, ...],
    ) -> None:
        """Process nodes matching only the TODO filter (any leaf status).

        Args:
            nodes: List of nodes to process
            is_todo_filter: If True, keep TODO nodes; if False, keep non-TODO
            callback: Function to call for each matching node
            callback_args: Extra arguments to pass to callback after (node,)
        """
        matching_nodes = [n for n in nodes if TodoHelper.is_todo(n) == is_todo_filter]

        for node in matching_nodes:
            callback(node, *callback_args)

    @staticmethod
    def process_hierarchical_order(
        node: xml.Element,
        callback: Callable[..., None],
        callback_args: Tuple[Any, ...],
    ) -> None:
        """Process node's children in 3-phase order: leaves, non-leaves, TODOs.

        Args:
            node: Parent node whose children to process
            callback: Function to call for each child (receives node + callback_args)
            callback_args: Extra arguments to pass to callback after (node,)
        """
        children = NodeTreeHelper.get_node_children(node)

        # Phase 1: Leaf items (non-TODO)
        HierarchicalNodeProcessor.process_hierarchical_phase(
            children,
            is_leaf_filter=True,
            is_todo_filter=False,
            callback=callback,
            callback_args=callback_args,
        )

        # Phase 2: Non-leaf children (non-TODO)
        HierarchicalNodeProcessor.process_hierarchical_phase(
            children,
            is_leaf_filter=False,
            is_todo_filter=False,
            callback=callback,
            callback_args=callback_args,
        )

        # Phase 3: TODO children (any leaf status)
        HierarchicalNodeProcessor.filter_and_process(
            children,
            is_todo_filter=True,
            callback=callback,
            callback_args=callback_args,
        )
