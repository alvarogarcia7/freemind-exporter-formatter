"""Value objects for mindmap date and time data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date as DateType
from typing import List

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
    end: DateTimeValue | None
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
