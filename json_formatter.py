from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml
import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class Formatter(MindmapExporter):
    def export(self, tree: xml.Element) -> None:
        result = self._convert_node_to_dict(tree)
        output = json.dumps(result, indent=2, ensure_ascii=False)
        print(output)

    def _convert_node_to_dict(self, node: xml.Element) -> Dict[str, Any]:
        node_dict: Dict[str, Any] = {}

        node_dict["tag"] = node.tag

        if node.attrib:
            node_dict["attributes"] = dict(node.attrib)

            if "TEXT" in node.attrib:
                node_dict["text"] = node.attrib["TEXT"]

            if "OBJECT" in node.attrib:
                parsed_object = self._parse_object_attribute(node.attrib["OBJECT"])
                if parsed_object:
                    node_dict["parsed_object"] = parsed_object

        children = [child for child in node if child.tag == "node"]
        if children:
            node_dict["children"] = []
            for child in children:
                node_dict["children"].append(self._convert_node_to_dict(child))

        worklog_data = self._extract_worklog_from_node(node)
        if worklog_data:
            node_dict["worklog"] = worklog_data

        return node_dict

    def _parse_object_attribute(self, object_str: str) -> Optional[Dict[str, Any]]:
        if "FormattedDate" not in object_str:
            return None

        parts = object_str.split("|")
        if len(parts) < 3:
            return None

        result: Dict[str, Any] = {
            "type": parts[0],
            "value": parts[1],
            "format": parts[2],
        }

        if parts[2] == "date":
            try:
                dt = datetime.strptime(parts[1].split("T")[0], "%Y-%m-%d")
                result["parsed_date"] = dt.date().isoformat()
            except ValueError:
                pass
        elif parts[2] == "datetime":
            try:
                datetime_str = parts[1]
                if "T" in datetime_str:
                    if "+" in datetime_str:
                        dt_part = datetime_str.split("+")[0]
                    elif "-" in datetime_str[11:]:
                        dt_part_list = datetime_str.split("-", 3)
                        if len(dt_part_list) >= 4:
                            dt_part = (
                                f"{dt_part_list[0]}-{dt_part_list[1]}-{dt_part_list[2]}"
                            )
                        else:
                            dt_part = datetime_str
                    else:
                        dt_part = datetime_str
                    dt = datetime.strptime(dt_part, "%Y-%m-%dT%H:%M")
                    result["parsed_datetime"] = dt.isoformat()
            except ValueError:
                pass

        return result

    def _extract_worklog_from_node(self, node: xml.Element) -> Optional[Dict[str, Any]]:
        obj_attr = node.get("OBJECT", "")

        if "FormattedDate" in obj_attr and "|date" in obj_attr:
            date_val = self._get_date_from_node(node)
            if not date_val:
                return None

            worklog_sections = []

            for child in node:
                if child.tag == "node" and child.get("TEXT") in ["WORKLOG", "TIMES"]:
                    section_data = self._extract_worklog_section(child)
                    if section_data:
                        worklog_sections.append(section_data)

            if worklog_sections:
                return {"date": date_val.isoformat(), "sections": worklog_sections}

        return None

    def _get_date_from_node(self, node: xml.Element) -> Optional[datetime]:
        obj_attr = node.get("OBJECT", "")
        if "FormattedDate" in obj_attr:
            parts = obj_attr.split("|")
            if len(parts) >= 2:
                date_str = parts[1]
                try:
                    dt = datetime.strptime(date_str.split("T")[0], "%Y-%m-%d")
                    return dt
                except ValueError:
                    pass
        return None

    def _extract_worklog_section(
        self, section_node: xml.Element
    ) -> Optional[Dict[str, Any]]:
        section_name = section_node.get("TEXT", "WORKLOG")
        entries: List[Dict[str, Any]] = []
        projects: List[Dict[str, Any]] = []

        for task_node in section_node:
            if task_node.tag != "node":
                continue

            if self._is_datetime_node(task_node):
                entry = self._extract_time_entry(task_node)
                if entry:
                    entries.append(entry)
            else:
                task_name = task_node.get("TEXT", "")

                has_direct_times = False
                has_subtasks = False

                for child in task_node:
                    if child.tag == "node":
                        if self._is_datetime_node(child):
                            has_direct_times = True
                        else:
                            child_has_times = any(
                                grandchild.tag == "node"
                                and self._is_datetime_node(grandchild)
                                for grandchild in child
                            )
                            if child_has_times:
                                has_subtasks = True

                if has_direct_times or has_subtasks:
                    project_data = self._extract_project_data(task_node, task_name)
                    if project_data:
                        projects.append(project_data)
                else:
                    entry = self._extract_time_entry(task_node)
                    if entry:
                        entries.append(entry)

        result: Dict[str, Any] = {"name": section_name}

        if projects:
            result["projects"] = projects

        if entries:
            result["entries"] = entries

        return result if (projects or entries) else None

    def _is_datetime_node(self, node: xml.Element) -> bool:
        obj_attr = node.get("OBJECT", "")
        return "FormattedDate" in obj_attr and "datetime" in obj_attr

    def _extract_project_data(
        self, project_node: xml.Element, project_name: str
    ) -> Optional[Dict[str, Any]]:
        project_data: Dict[str, Any] = {"name": project_name}
        tasks: List[Dict[str, Any]] = []

        has_direct_times = any(
            child.tag == "node" and self._is_datetime_node(child)
            for child in project_node
        )

        if has_direct_times:
            time_entries = self._extract_task_time_entries(project_node)
            if time_entries:
                tasks.append({"name": "", "entries": time_entries})
        else:
            for child in project_node:
                if child.tag == "node" and not self._is_datetime_node(child):
                    child_name = child.get("TEXT", "")
                    time_entries = self._extract_task_time_entries(child)
                    if time_entries:
                        tasks.append({"name": child_name, "entries": time_entries})

        if tasks:
            project_data["tasks"] = tasks
            return project_data

        return None

    def _extract_task_time_entries(
        self, task_node: xml.Element
    ) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []

        for child in task_node:
            if child.tag == "node" and self._is_datetime_node(child):
                entry = self._extract_time_entry(child)
                if entry:
                    entries.append(entry)

        return entries

    def _extract_time_entry(self, time_node: xml.Element) -> Optional[Dict[str, Any]]:
        start_time = self._parse_datetime_from_node(time_node)
        if not start_time:
            task_text = time_node.get("TEXT", "")
            return {"task": task_text, "start": None, "end": None}

        entry: Dict[str, Any] = {"start": start_time.isoformat()}

        end_time = None
        comments: List[str] = []
        task_description = None

        for child in time_node:
            if child.tag == "node":
                child_time = self._parse_datetime_from_node(child)
                if child_time:
                    if not end_time:
                        end_time = child_time
                    for grandchild in child:
                        if grandchild.tag == "node":
                            text = grandchild.get("TEXT", "")
                            if text:
                                comments.append(text)
                else:
                    text = child.get("TEXT", "")
                    if text:
                        if not task_description:
                            task_description = text
                        else:
                            comments.append(text)

        if end_time:
            entry["end"] = end_time.isoformat()
        else:
            entry["end"] = None

        if task_description:
            entry["task"] = task_description

        if comments:
            entry["comments"] = comments

        return entry

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
                        elif "-" in datetime_str[11:]:
                            dt_parts = datetime_str.split("-")
                            if len(dt_parts) >= 3:
                                dt_part = f"{dt_parts[0]}-{dt_parts[1]}-{dt_parts[2]}"
                            else:
                                dt_part = datetime_str
                        else:
                            dt_part = datetime_str
                        return datetime.strptime(dt_part, "%Y-%m-%dT%H:%M")
                except ValueError:
                    pass
        return None
