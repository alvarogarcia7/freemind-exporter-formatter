"""
Value objects for ORGMode date reading and processing.

This module extracts date-related logic into immutable dataclasses
that represent dates, datetimes, and date entries with their sections.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from datetime import date as DateType
from typing import Optional, List, Any
import xml.etree.ElementTree as xml


@dataclass(frozen=True)
class DateValue:
    """Represents a date extracted from a mindmap node."""

    value: DateType

    def format_header(self) -> str:
        """Format date as ORGMode header: [YYYY-MM-DD Day]"""
        return f"[{self.value.strftime('%Y-%m-%d %a')}]"


@dataclass(frozen=True)
class DateTimeValue:
    """Represents a datetime extracted from a mindmap node."""

    value: datetime

    def format_time(self) -> str:
        """Format time portion: HH:MM"""
        return self.value.strftime("%H:%M")


@dataclass(frozen=True)
class TimeEntry:
    """Represents a time entry in the TIMES section."""

    start: DateTimeValue
    end: Optional[DateTimeValue]
    description: str
    tags: List[str]

    def format_line(self) -> str:
        """Format as ORGMode time entry: - HH:MM - HH:MM: description :tags:"""
        start_str = self.start.format_time()
        end_str = self.end.format_time() if self.end else "noend"

        desc_clean = self.description.strip() if self.description else ""
        tags_str = f" :{':'.join(self.tags)}:" if self.tags else ""

        if desc_clean:
            return f"- {start_str} - {end_str}: {desc_clean}{tags_str}"
        else:
            return f"- {start_str} - {end_str}{tags_str}"


@dataclass(frozen=True)
class Section:
    """Represents a section (WORKLOG, TIMES, TODO, etc.) with its content."""

    name: str
    node: xml.Element

    def is_times_section(self) -> bool:
        return self.name == "TIMES"

    def is_todo_section(self) -> bool:
        return self.name == "TODO"


@dataclass(frozen=True)
class DateEntry:
    """Represents a date with its associated sections."""

    date: DateValue
    sections: List[Section]

    def sort_key(self) -> DateType:
        """Return the date value for sorting."""
        return self.date.value


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


@dataclass(frozen=True)
class TaskEntry:
    """Represents a worklog or time-tracking task entry."""

    task_name: str
    start: datetime
    end: Optional[datetime]
    date: DateType
    tags: List[str]
    section_name: str = "WORKLOG"
    comments: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class TaskInfo:
    """Represents a task within a project with time entries."""

    task_name: str
    entries: List[dict[str, Any]]  # List of {start, end, comments}
    tags: List[str]


@dataclass(frozen=True)
class ProjectInfo:
    """Represents a project containing multiple tasks."""

    name: str
    tasks: List[TaskInfo]
    tags: List[str]


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
