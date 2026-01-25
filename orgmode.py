from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple


class Formatter(MindmapExporter):
    def parse(self, tree: xml.Element) -> None:
        date_nodes = self._find_all_date_nodes(tree)
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
                            time_str = self._format_time_entry(entry)
                            lines.append(f"- {time_str}")

                        # Calculate and display subtotal for this task if there are multiple tasks
                        if has_multiple_tasks and task_info["task_name"]:
                            task_total_minutes = sum(
                                self._calculate_duration_minutes(e)
                                for e in entries_for_date
                            )
                            if task_total_minutes > 0:
                                subtotal_str = self._format_duration(task_total_minutes)
                                lines.append(f"Subtotal: {subtotal_str}")

                        if task_info["task_name"]:
                            lines.append("")

                    total_minutes = self._calculate_project_total(project_info)
                    if total_minutes > 0:
                        total_str = self._format_duration(total_minutes)
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
                        time_str = self._format_worklog_entry(entry)
                        lines.append(f"- {time_str}")

                    total_minutes = sum(
                        self._calculate_duration_minutes(entry) for entry in entries
                    )
                    if total_minutes > 0:
                        total_str = self._format_duration(total_minutes)
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

    def _find_all_date_nodes(self, root: xml.Element) -> List[xml.Element]:
        date_nodes: List[xml.Element] = []
        self._find_date_nodes_recursive(root, date_nodes)
        return date_nodes

    def _find_date_nodes_recursive(
        self, node: xml.Element, date_nodes: List[xml.Element]
    ) -> None:
        obj_attr = node.get("OBJECT", "")
        if "FormattedDate" in obj_attr and "|date" in obj_attr:
            date_nodes.append(node)

        for child in node:
            if child.tag == "node":
                self._find_date_nodes_recursive(child, date_nodes)

    def _extract_all_data(
        self, date_nodes: List[xml.Element]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[date]]:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen: List[date] = []

        for date_node in date_nodes:
            date_val = self._get_date_from_node(date_node)
            if not date_val:
                continue

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

    def _get_date_from_node(self, node: xml.Element) -> Optional[date]:
        obj_attr = node.get("OBJECT", "")
        if "FormattedDate" in obj_attr:
            parts = obj_attr.split("|")
            if len(parts) >= 2:
                date_str = parts[1]
                try:
                    dt = datetime.strptime(date_str.split("T")[0], "%Y-%m-%d")
                    return dt.date()
                except ValueError:
                    pass
        return None

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

                if self._is_datetime_node(task_node):
                    start_time = self._parse_datetime_from_node(task_node)
                    if start_time:
                        end_time = self._find_end_time(task_node)
                        task_description, _ = self._get_task_description(task_node)
                        tags = self._extract_tags_from_node(task_node)

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
                            if self._is_datetime_node(child):
                                has_direct_times = True
                            elif not self._is_datetime_node(child):
                                child_has_times = False
                                for grandchild in child:
                                    if (
                                        grandchild.tag == "node"
                                        and self._is_datetime_node(grandchild)
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
                            "tags": self._extract_tags_from_node(task_node),
                        }

                        if has_direct_times:
                            task_entries = self._extract_task_entries(task_node)
                            if task_entries:
                                project_info["tasks"].append(
                                    {
                                        "task_name": "",
                                        "entries": task_entries,
                                        # also attach tags to this task entry so downstream code can use them if needed
                                        "tags": self._extract_tags_from_node(task_node),
                                    }
                                )
                        elif has_subtasks:
                            for child in task_node:
                                if child.tag == "node" and not self._is_datetime_node(
                                    child
                                ):
                                    child_name = child.get("TEXT", "")
                                    task_entries = self._extract_task_entries(child)
                                    if task_entries:
                                        project_info["tasks"].append(
                                            {
                                                "task_name": child_name,
                                                "entries": task_entries,
                                                "tags": self._extract_tags_from_node(
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

    def _is_datetime_node(self, node: xml.Element) -> bool:
        obj_attr = node.get("OBJECT", "")
        return "FormattedDate" in obj_attr and "datetime" in obj_attr

    def _extract_task_entries(self, task_node: xml.Element) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []

        for child in task_node:
            if child.tag == "node":
                start_time = self._parse_datetime_from_node(child)
                if start_time:
                    end_time = self._find_end_time(child)
                    comments = self._extract_comments(child)

                    entries.append(
                        {"start": start_time, "end": end_time, "comments": comments}
                    )

        return entries

    def _parse_datetime_from_node(self, node: xml.Element) -> Optional[datetime]:
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
                        return datetime.strptime(dt_part, "%Y-%m-%dT%H:%M")
                except ValueError:
                    pass
        return None

    def _find_end_time(self, start_node: xml.Element) -> Optional[datetime]:
        for child in start_node:
            if child.tag == "node":
                end_time = self._parse_datetime_from_node(child)
                if end_time:
                    return end_time
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
                    child_time = self._parse_datetime_from_node(child)
                    if not child_time:
                        text = child.get("TEXT", "").strip()
                        if text:
                            return text, tags
                    else:
                        for grandchild in child:
                            if grandchild.tag == "node":
                                grandchild_time = self._parse_datetime_from_node(
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

    def _calculate_duration_minutes(self, entry: Dict[str, Any]) -> int:
        if entry["end"] is None:
            return 0
        delta = entry["end"] - entry["start"]
        return int(delta.total_seconds() / 60)

    def _format_duration(self, total_minutes: int) -> str:
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

    def _calculate_project_total(self, project_info: Dict[str, Any]) -> int:
        total_minutes = 0
        for task_info in project_info["tasks"]:
            for entry in task_info["entries"]:
                total_minutes += self._calculate_duration_minutes(entry)
        return total_minutes

    def _format_time_entry(self, entry: Dict[str, Any]) -> str:
        start_str = entry["start"].strftime("%H:%M")
        if entry["end"]:
            end_str = entry["end"].strftime("%H:%M")
            result = f"{start_str} - {end_str}"
        else:
            result = f"{start_str} -"

        if entry["comments"]:
            for comment in entry["comments"]:
                result += f" ; {comment}"

        return result

    def _format_worklog_entry(self, entry: Dict[str, Any]) -> str:
        start_str = entry["start"].strftime("%H:%M")
        if entry["end"]:
            end_str = entry["end"].strftime("%H:%M")
            result = f"{start_str} - {end_str}: {entry['task_name']}"
        else:
            task_name = entry["task_name"]
            if task_name:
                result = f"{start_str} - noend: {task_name}"
            else:
                result = f"{start_str} - noend:"

        return result
