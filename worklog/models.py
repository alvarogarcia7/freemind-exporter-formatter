"""Value objects for worklog task and project data."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date as DateType
from typing import List, Any


@dataclass(frozen=True)
class TaskEntry:
    """Represents a worklog or time-tracking task entry."""

    task_name: str
    start: datetime
    end: datetime | None
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
