from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
from mindmap.reader import DateReader, DateTimeReader, NodeTreeHelper
from worklog.helpers import DurationFormatter
from worklog.format import TodoHelper


class Formatter(MindmapExporter, NodeTreeHelper):
    def parse(self, tree: xml.Element) -> None:
        date_nodes = DateReader.find_all_date_nodes(tree)
        all_projects, all_worklog_entries, dates_seen = self._extract_all_data(
            date_nodes
        )
        self.result = (all_projects, all_worklog_entries, dates_seen)

    def format(self) -> list[str]:
        if self.result is None:
            return []
        all_projects, all_worklog_entries, dates_seen = self.result
        return self._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

    def _format_orgmode_output(
        self,
        all_projects: List[Dict[str, Any]],
        all_worklog_entries: List[Dict[str, Any]],
        dates_seen: List[date],
    ) -> list[str]:
        """Format the extracted data into orgmode output lines."""
        lines: List[str] = []
        sorted_dates = sorted(dates_seen)

        all_worklog_entries_sorted = sorted(
            all_worklog_entries, key=lambda e: e["start"]
        )
        for i in range(len(all_worklog_entries_sorted) - 1):
            if all_worklog_entries_sorted[i]["end"] is None:
                next_entry = all_worklog_entries_sorted[i + 1]
                if all_worklog_entries_sorted[i]["date"] == next_entry["date"]:
                    all_worklog_entries_sorted[i]["end"] = next_entry["start"]

        lines.append("* PROJ Worklog")

        for date_val in sorted_dates:
            formatted_date = date_val.strftime("%Y-%m-%d %a")
            lines.append(f"** PROJ [{formatted_date}]")

            # Filter projects to only those with entries on this date
            projects_for_date = []
            for project_info in all_projects:
                project_has_entries_on_date = False
                for task_info in project_info["tasks"]:
                    for entry in task_info["entries"]:
                        if entry["start"].date() == date_val:
                            project_has_entries_on_date = True
                            break
                    if project_has_entries_on_date:
                        break
                if project_has_entries_on_date:
                    projects_for_date.append(project_info)

            if projects_for_date:
                lines.append("*** PROJ Projects")

                for idx, project_info in enumerate(projects_for_date):
                    name = project_info["name"]
                    project_name = name
                    # include project-level tags (icons) if present
                    if "tags" in project_info and project_info["tags"]:
                        proj_tags = f" :{':'.join(project_info['tags'])}:"
                    else:
                        proj_tags = ""
                    lines.append(f"**** PROJ {project_name}{proj_tags}")

                    # Check if project has multiple tasks with entries on this date
                    tasks_with_entries_on_date = []
                    for task_info in project_info["tasks"]:
                        entries_for_date = [
                            e
                            for e in task_info["entries"]
                            if e["start"].date() == date_val
                        ]
                        if entries_for_date:
                            tasks_with_entries_on_date.append(
                                (task_info, entries_for_date)
                            )

                    has_multiple_tasks = len(tasks_with_entries_on_date) > 1

                    for task_info, entries_for_date in tasks_with_entries_on_date:
                        if "tags" in task_info and task_info["tags"]:
                            formatted_tags = f":{':'.join(task_info['tags'])}:"
                        else:
                            formatted_tags = ""
                        if task_info["task_name"]:
                            lines.append(
                                f"***** {task_info['task_name']}{formatted_tags}"
                            )

                        for entry in entries_for_date:
                            time_str = DurationFormatter.format_time_entry(entry)
                            lines.append(f"- {time_str}")

                        # Calculate and display subtotal for this task if there are multiple tasks
                        if has_multiple_tasks and task_info["task_name"]:
                            task_total_minutes = sum(
                                DurationFormatter.calculate_duration_minutes(e)
                                for e in entries_for_date
                            )
                            if task_total_minutes > 0:
                                subtotal_str = DurationFormatter.format_duration(
                                    task_total_minutes
                                )
                                lines.append(f"Subtotal: {subtotal_str}")

                        if task_info["task_name"]:
                            lines.append("")

                    total_minutes = self._calculate_project_total(project_info)
                    if total_minutes > 0:
                        total_str = DurationFormatter.format_duration(total_minutes)
                        lines.append(f"Total: {total_str}")

                    # Print blank line between projects (except after the last project)
                    if idx < len(projects_for_date) - 1:
                        lines.append("")

            worklog_entries_for_date = [
                e for e in all_worklog_entries_sorted if e["start"].date() == date_val
            ]
            if worklog_entries_for_date:
                sections_dict: Dict[str, List[Dict[str, Any]]] = {}
                for entry in worklog_entries_for_date:
                    section_name = entry.get("section_name", "WORKLOG")
                    if section_name not in sections_dict:
                        sections_dict[section_name] = []
                    sections_dict[section_name].append(entry)

                for section_name, entries in sections_dict.items():
                    lines.append(f"*** PROJ {section_name}")
                    for entry in entries:
                        time_str = DurationFormatter.format_worklog_entry(entry)
                        lines.append(f"- {time_str}")

                    total_minutes = sum(
                        DurationFormatter.calculate_duration_minutes(entry)
                        for entry in entries
                    )
                    if total_minutes > 0:
                        total_str = DurationFormatter.format_duration(total_minutes)
                        lines.append(f"Total: {total_str}")

            # Add blank lines between dates
            is_last_date = date_val == sorted_dates[-1]
            has_content = worklog_entries_for_date or projects_for_date

            # Print blank line(s) after each date section
            if not has_content:
                # Empty date: 2 blank lines
                lines.append("")
                lines.append("")
            elif is_last_date:
                # Last date: 2 blank lines
                lines.append("")
                lines.append("")
            else:
                # Regular dates: 1 blank line
                lines.append("")

        return lines

    def _extract_all_data(
        self, date_nodes: List[xml.Element]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[date]]:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen: List[date] = []

        for date_node in date_nodes:
            date_val_obj = DateReader.read_date(date_node)
            if not date_val_obj:
                continue

            date_val = date_val_obj.value
            if date_val not in dates_seen:
                dates_seen.append(date_val)

            for child in date_node:
                if child.tag == "node" and child.get("TEXT") in ["WORKLOG", "TIMES"]:
                    section_name = child.get("TEXT", "WORKLOG")
                    self._extract_from_worklog(
                        child,
                        all_projects,
                        all_worklog_entries,
                        dates_seen,
                        section_name,
                    )

        return all_projects, all_worklog_entries, dates_seen

    def _extract_from_worklog(
        self,
        worklog_node: xml.Element,
        all_projects: List[Dict[str, Any]],
        all_worklog_entries: List[Dict[str, Any]],
        dates_seen: List[date],
        section_name: str = "WORKLOG",
    ) -> None:
        for task_node in worklog_node:
            if task_node.tag == "node":
                task_name = task_node.get("TEXT", "")

                if DateTimeReader.is_datetime_node(task_node):
                    start_time_val = DateTimeReader.read_datetime(task_node)
                    if start_time_val:
                        start_time = start_time_val.value
                        end_time = self._find_end_time(task_node)
                        task_description, _ = self._get_task_description(task_node)
                        tags = NodeTreeHelper.extract_tags_from_node(task_node)

                        entry_date = start_time.date()
                        if entry_date not in dates_seen:
                            dates_seen.append(entry_date)

                        all_worklog_entries.append(
                            {
                                "task_name": task_description,
                                "start": start_time,
                                "end": end_time,
                                "date": entry_date,
                                "tags": tags,
                                "section_name": section_name,
                            }
                        )
                else:
                    has_direct_times = False
                    has_subtasks = False

                    for child in task_node:
                        if child.tag == "node":
                            if DateTimeReader.is_datetime_node(child):
                                has_direct_times = True
                            elif not DateTimeReader.is_datetime_node(child):
                                child_has_times = False
                                for grandchild in child:
                                    if (
                                        grandchild.tag == "node"
                                        and DateTimeReader.is_datetime_node(grandchild)
                                    ):
                                        child_has_times = True
                                        break
                                if child_has_times:
                                    has_subtasks = True

                    if has_direct_times or has_subtasks:
                        project_info: Dict[str, Any] = {
                            "name": task_name,
                            "tasks": [],
                            # attach tags from the project node itself (if any icons are present)
                            "tags": NodeTreeHelper.extract_tags_from_node(task_node),
                        }

                        if has_direct_times:
                            task_entries = self._extract_task_entries(task_node)
                            if task_entries:
                                project_info["tasks"].append(
                                    {
                                        "task_name": "",
                                        "entries": task_entries,
                                        # also attach tags to this task entry so downstream code can use them if needed
                                        "tags": NodeTreeHelper.extract_tags_from_node(
                                            task_node
                                        ),
                                    }
                                )
                        elif has_subtasks:
                            for child in task_node:
                                if (
                                    child.tag == "node"
                                    and not DateTimeReader.is_datetime_node(child)
                                ):
                                    child_name = child.get("TEXT", "")
                                    task_entries = self._extract_task_entries(child)
                                    if task_entries:
                                        project_info["tasks"].append(
                                            {
                                                "task_name": child_name,
                                                "entries": task_entries,
                                                "tags": NodeTreeHelper.extract_tags_from_node(
                                                    child
                                                ),
                                            }
                                        )

                        if project_info["tasks"]:
                            project_exists = False
                            for existing_project in all_projects:
                                if existing_project["name"] == project_info["name"]:
                                    project_exists = True
                                    break
                            if not project_exists:
                                all_projects.append(project_info)

    def _extract_task_entries(self, task_node: xml.Element) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []

        for child in task_node:
            if child.tag == "node":
                start_time_val = DateTimeReader.read_datetime(child)
                if start_time_val:
                    start_time = start_time_val.value
                    end_time = self._find_end_time(child)
                    comments = self._extract_comments(child)

                    entries.append(
                        {"start": start_time, "end": end_time, "comments": comments}
                    )

        return entries

    def _find_end_time(self, start_node: xml.Element) -> Optional[datetime]:
        """Find end time in children of a datetime node."""
        for child in start_node:
            if child.tag == "node":
                end_time_val = DateTimeReader.read_datetime(child)
                if end_time_val:
                    return end_time_val.value
        return None

    def _get_task_description(self, time_node: xml.Element) -> tuple[str, list[str]]:
        children = list(time_node)
        if len(children) >= 1:
            tags = []
            for child in children:
                if child.tag == "icon":
                    tags.append(
                        "".join(
                            list(
                                map(
                                    lambda x: x.title(),
                                    child.attrib["BUILTIN"].split("-"),
                                )
                            )
                        )
                    )
                elif child.tag == "node":
                    child_time = DateTimeReader.read_datetime(child)
                    if not child_time:
                        text = child.get("TEXT", "").strip()
                        if text:
                            return text, tags
                    else:
                        for grandchild in child:
                            if grandchild.tag == "node":
                                grandchild_time = DateTimeReader.read_datetime(
                                    grandchild
                                )
                                if not grandchild_time:
                                    text = grandchild.get("TEXT", "").strip()
                                    if text:
                                        return text, tags
        return "", []

    def _extract_comments(self, node: xml.Element) -> List[str]:
        comments: List[str] = []
        for child in node:
            if child.tag == "node":
                dt = self._parse_datetime_from_node(child)
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

    def _extract_tags_from_node(self, node: xml.Element) -> List[str]:
        """Extract icon tags from a node and convert BUILTIN names to TitleCase without separators.

        Example: BUILTIN="stop-sign" -> "StopSign". Returns an empty list if no icons present.
        """
        tags: List[str] = []
        for child in node:
            if child.tag == "icon":
                builtin = child.attrib.get("BUILTIN", "")
                if builtin:
                    parts = builtin.split("-")
                    tags.append("".join([p.title() for p in parts]))
        return tags

    def _calculate_project_total(self, project_info: Dict[str, Any]) -> int:
        total_minutes = 0
        for task_info in project_info["tasks"]:
            for entry in task_info["entries"]:
                total_minutes += DurationFormatter.calculate_duration_minutes(entry)
        return total_minutes

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

    # ========== Backward-compatible wrapper methods (delegate to NodeTreeHelper and DurationFormatter) ==========

    def _is_leaf(self, node: xml.Element) -> bool:
        """Backward-compatible wrapper for NodeTreeHelper.is_leaf()."""
        return NodeTreeHelper.is_leaf(node)

    def _is_todo(self, node: xml.Element) -> bool:
        """Backward-compatible wrapper for TodoHelper.is_todo()."""
        return TodoHelper.is_todo(node)

    def _get_node_children(self, node: xml.Element) -> List[xml.Element]:
        """Backward-compatible wrapper for NodeTreeHelper.get_node_children()."""
        return NodeTreeHelper.get_node_children(node)

    def _calculate_duration_minutes(self, entry: Dict[str, Any]) -> int:
        """Backward-compatible wrapper for DurationFormatter.calculate_duration_minutes()."""
        return DurationFormatter.calculate_duration_minutes(entry)

    def _format_duration(self, total_minutes: int) -> str:
        """Backward-compatible wrapper for DurationFormatter.format_duration()."""
        return DurationFormatter.format_duration(total_minutes)

    def _format_time_entry(self, entry: Dict[str, Any]) -> str:
        """Backward-compatible wrapper for DurationFormatter.format_time_entry()."""
        return DurationFormatter.format_time_entry(entry)

    def _format_worklog_entry(self, entry: Dict[str, Any]) -> str:
        """Backward-compatible wrapper for DurationFormatter.format_worklog_entry()."""
        return DurationFormatter.format_worklog_entry(entry)
