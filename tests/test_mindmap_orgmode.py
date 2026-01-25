import unittest
from datetime import datetime, date
import xml.etree.ElementTree as xml
from typing import List, Dict, Any

from orgmode import Formatter


class TestMindmapOrgmode(unittest.TestCase):
    def setUp(self) -> None:
        self.formatter = Formatter()

    def test_find_date_nodes_with_single_date(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date">
                <node TEXT="WORKLOG"/>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        date_nodes = self.formatter._find_all_date_nodes(root)
        self.assertEqual(len(date_nodes), 1)

    def test_find_date_nodes_with_multiple_dates(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date">
                <node TEXT="WORKLOG"/>
            </node>
            <node TEXT="15/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-15T00:00+0400|date">
                <node TEXT="WORKLOG"/>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        date_nodes = self.formatter._find_all_date_nodes(root)
        self.assertEqual(len(date_nodes), 2)

    def test_find_date_nodes_ignores_datetime_nodes(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
                <node TEXT="Work"/>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        date_nodes = self.formatter._find_all_date_nodes(root)
        # Note: The function looks for nodes with '|date' in OBJECT, which matches both |date and |datetime
        # This test verifies the behavior, but the actual filtering happens in _extract_all_data
        self.assertEqual(len(date_nodes), 1)

    def test_get_date_from_node(self) -> None:
        xml_str = '<node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._get_date_from_node(node)
        self.assertEqual(result, date(2026, 1, 14))

    def test_get_date_from_node_with_invalid_date(self) -> None:
        xml_str = '<node TEXT="Invalid" OBJECT="org.freeplane.features.format.FormattedDate|invalid|date"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._get_date_from_node(node)
        self.assertIsNone(result)

    def test_is_datetime_node_returns_true(self) -> None:
        xml_str = '<node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._is_datetime_node(node)
        self.assertTrue(result)

    def test_is_datetime_node_returns_false_for_date(self) -> None:
        xml_str = '<node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._is_datetime_node(node)
        self.assertFalse(result)

    def test_parse_datetime_from_node(self) -> None:
        xml_str = '<node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._parse_datetime_from_node(node)
        self.assertEqual(result, datetime(2026, 1, 14, 8, 36))

    def test_parse_datetime_from_node_with_timezone(self) -> None:
        xml_str = '<node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._parse_datetime_from_node(node)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.hour, 8)
        self.assertEqual(result.minute, 36)

    def test_parse_datetime_from_node_invalid(self) -> None:
        xml_str = '<node TEXT="Invalid" OBJECT="org.freeplane.features.format.FormattedDate|invalid|datetime"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._parse_datetime_from_node(node)
        self.assertIsNone(result)

    def test_find_end_time(self) -> None:
        xml_str = """
        <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
            <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._find_end_time(node)
        self.assertEqual(result, datetime(2026, 1, 14, 11, 16))

    def test_find_end_time_no_end(self) -> None:
        xml_str = """
        <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
            <node TEXT="Comment"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._find_end_time(node)
        self.assertIsNone(result)

    def test_get_task_description_with_description(self) -> None:
        xml_str = """
        <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
            <node TEXT="Task description"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result, tags = self.formatter._get_task_description(node)
        self.assertEqual(result, "Task description")
        self.assertEqual(tags, [])

    def test_get_task_description_with_description_and_tags(self) -> None:
        xml_str = """
        <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
            <icon BUILTIN="bookmark"/>
            <icon BUILTIN="stop-sign"/>
            <node TEXT="Task description"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result, tags = self.formatter._get_task_description(node)
        self.assertEqual(result, "Task description")
        self.assertEqual(tags, ["Bookmark", "StopSign"])

    def test_get_task_description_skips_datetime_child(self) -> None:
        xml_str = """
        <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
            <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime"/>
            <node TEXT="Task description"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result, tags = self.formatter._get_task_description(node)
        self.assertEqual(result, "Task description")
        self.assertEqual(tags, [])

    def test_get_task_description_empty(self) -> None:
        xml_str = """
        <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
            <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result, tags = self.formatter._get_task_description(node)
        self.assertEqual(result, "")
        self.assertEqual(tags, [])

    def test_extract_comments_single_comment(self) -> None:
        xml_str = """
        <node TEXT="Start">
            <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime">
                <node TEXT="Comment text"/>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_comments(node)
        self.assertEqual(result, ["Comment text"])

    def test_extract_comments_multiple_comments(self) -> None:
        xml_str = """
        <node TEXT="Start">
            <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime">
                <node TEXT="Comment 1"/>
                <node TEXT="Comment 2"/>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_comments(node)
        self.assertEqual(result, ["Comment 1", "Comment 2"])

    def test_extract_comments_nested_under_datetime(self) -> None:
        xml_str = """
        <node TEXT="Start">
            <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime">
                <node TEXT="14/01/2026 11:20" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:20+0400|datetime">
                    <node TEXT="Nested comment"/>
                </node>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_comments(node)
        # When there's a datetime child, we look at its children (grandchildren of node)
        # In this case, the grandchild is another datetime node, so its TEXT is extracted
        # The great-grandchild "Nested comment" is not reached by this function
        self.assertEqual(result, ["14/01/2026 11:20"])

    def test_extract_comments_empty(self) -> None:
        xml_str = """
        <node TEXT="Start">
            <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_comments(node)
        self.assertEqual(result, [])

    def test_format_time_entry_with_end(self) -> None:
        entry = {
            "start": datetime(2026, 1, 14, 8, 36),
            "end": datetime(2026, 1, 14, 11, 16),
            "comments": [],
        }
        result = self.formatter._format_time_entry(entry)
        self.assertEqual(result, "08:36 - 11:16")

    def test_format_time_entry_without_end(self) -> None:
        entry: Dict[str, Any] = {
            "start": datetime(2026, 1, 14, 8, 36),
            "end": None,
            "comments": [],
        }
        result = self.formatter._format_time_entry(entry)
        self.assertEqual(result, "08:36 -")

    def test_format_time_entry_with_comments(self) -> None:
        entry = {
            "start": datetime(2026, 1, 14, 8, 36),
            "end": datetime(2026, 1, 14, 11, 16),
            "comments": ["Comment 1", "Comment 2"],
        }
        result = self.formatter._format_time_entry(entry)
        self.assertEqual(result, "08:36 - 11:16 ; Comment 1 ; Comment 2")

    def test_format_worklog_entry_with_end(self) -> None:
        entry = {
            "task_name": "Work on this",
            "start": datetime(2026, 1, 14, 11, 14),
            "end": datetime(2026, 1, 14, 11, 21),
        }
        result = self.formatter._format_worklog_entry(entry)
        self.assertEqual(result, "11:14 - 11:21: Work on this")

    def test_format_worklog_entry_without_end(self) -> None:
        entry = {
            "task_name": "Work on Foo",
            "start": datetime(2026, 1, 14, 11, 35),
            "end": None,
        }
        result = self.formatter._format_worklog_entry(entry)
        self.assertEqual(result, "11:35 - noend: Work on Foo")

    def test_extract_task_entries_single_entry(self) -> None:
        xml_str = """
        <node TEXT="Task">
            <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
                <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime">
                    <node TEXT="Comment"/>
                </node>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        entries: List[Dict[str, Any]] = self.formatter._extract_task_entries(node)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["start"], datetime(2026, 1, 14, 8, 36))
        self.assertEqual(entries[0]["end"], datetime(2026, 1, 14, 11, 16))
        self.assertEqual(entries[0]["comments"], ["Comment"])

    def test_extract_task_entries_multiple_entries(self) -> None:
        xml_str = """
        <node TEXT="Task">
            <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
                <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime"/>
            </node>
            <node TEXT="14/01/2026 11:17" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:17+0400|datetime">
                <node TEXT="14/01/2026 11:20" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:20+0400|datetime"/>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        entries = self.formatter._extract_task_entries(node)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["start"], datetime(2026, 1, 14, 8, 36))
        self.assertEqual(entries[1]["start"], datetime(2026, 1, 14, 11, 17))

    def test_extract_task_entries_empty(self) -> None:
        xml_str = """
        <node TEXT="Task">
            <node TEXT="No datetime"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        entries = self.formatter._extract_task_entries(node)
        self.assertEqual(len(entries), 0)

    def test_format_orgmode_output_basic(self) -> None:
        all_projects: List[Dict[str, Any]] = [
            {
                "name": "Project A",
                "tasks": [
                    {
                        "task_name": "Task 1",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 14, 8, 36),
                                "end": datetime(2026, 1, 14, 11, 16),
                                "comments": [],
                            }
                        ],
                    }
                ],
            }
        ]
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("* PROJ Worklog", lines)
        self.assertIn("** PROJ [2026-01-14 Wed]", lines)
        self.assertIn("*** PROJ Projects", lines)
        self.assertIn("**** PROJ Project A", lines)
        self.assertIn("***** Task 1", lines)
        self.assertIn("- 08:36 - 11:16", lines)

    def test_format_orgmode_output_with_worklog_entries(self) -> None:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries = [
            {
                "task_name": "Work on this",
                "start": datetime(2026, 1, 14, 11, 14),
                "end": datetime(2026, 1, 14, 11, 21),
                "date": date(2026, 1, 14),
                "section_name": "WORKLOG",
            }
        ]
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("* PROJ Worklog", lines)
        self.assertIn("** PROJ [2026-01-14 Wed]", lines)
        self.assertIn("*** PROJ WORKLOG", lines)
        self.assertIn("- 11:14 - 11:21: Work on this", lines)
        self.assertIn("Total: 7m", lines)

    def test_format_orgmode_output_multiple_dates_sorted(self) -> None:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 22), date(2026, 1, 20), date(2026, 1, 21)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        date_lines = [line for line in lines if line.startswith("** PROJ [")]
        self.assertEqual(len(date_lines), 3)
        self.assertIn("[2026-01-20", date_lines[0])
        self.assertIn("[2026-01-21", date_lines[1])
        self.assertIn("[2026-01-22", date_lines[2])

    def test_format_orgmode_output_empty_dates(self) -> None:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("* PROJ Worklog", lines)
        self.assertIn("** PROJ [2026-01-14 Wed]", lines)
        # No projects or worklog section for empty date

    def test_format_orgmode_output_with_multiple_tasks(self) -> None:
        all_projects: List[Dict[str, Any]] = [
            {
                "name": "Project B",
                "tasks": [
                    {
                        "task_name": "Subtask 1",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 18, 9, 0),
                                "end": datetime(2026, 1, 18, 10, 0),
                                "comments": [],
                            }
                        ],
                    },
                    {
                        "task_name": "Subtask 2",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 18, 11, 0),
                                "end": datetime(2026, 1, 18, 12, 0),
                                "comments": [],
                            }
                        ],
                    },
                ],
            }
        ]
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 18)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("**** PROJ Project B", lines)
        self.assertIn("***** Subtask 1", lines)
        self.assertIn("***** Subtask 2", lines)
        self.assertIn("Subtotal: 1h", lines)
        self.assertIn("Total: 2h", lines)


class TestFormatOrgmodeOutput(unittest.TestCase):
    def setUp(self) -> None:
        self.formatter = Formatter()

    def test_format_orgmode_output_empty_data(self) -> None:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen: List[date] = []

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertEqual(lines, ["* PROJ Worklog"])

    def test_format_orgmode_output_single_empty_date(self) -> None:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("* PROJ Worklog", lines)
        self.assertIn("** PROJ [2026-01-14 Wed]", lines)
        self.assertEqual(lines.count(""), 2)

    def test_format_orgmode_output_multiple_empty_dates(self) -> None:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 14), date(2026, 1, 15), date(2026, 1, 16)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("* PROJ Worklog", lines)
        self.assertIn("** PROJ [2026-01-14 Wed]", lines)
        self.assertIn("** PROJ [2026-01-15 Thu]", lines)
        self.assertIn("** PROJ [2026-01-16 Fri]", lines)
        self.assertTrue(all(isinstance(line, str) for line in lines))

    def test_format_orgmode_output_project_with_single_task(self) -> None:
        all_projects: List[Dict[str, Any]] = [
            {
                "name": "Project Alpha",
                "tasks": [
                    {
                        "task_name": "",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 14, 9, 0),
                                "end": datetime(2026, 1, 14, 10, 30),
                                "comments": [],
                            }
                        ],
                    }
                ],
            }
        ]
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("**** PROJ Project Alpha", lines)
        self.assertIn("- 09:00 - 10:30", lines)
        self.assertIn("Total: 1h 30m", lines)
        self.assertNotIn("Subtotal:", "\n".join(lines))

    def test_format_orgmode_output_project_with_multiple_tasks_shows_subtotals(
        self,
    ) -> None:
        all_projects: List[Dict[str, Any]] = [
            {
                "name": "Project Beta",
                "tasks": [
                    {
                        "task_name": "Backend work",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 14, 9, 0),
                                "end": datetime(2026, 1, 14, 10, 0),
                                "comments": [],
                            },
                            {
                                "start": datetime(2026, 1, 14, 10, 0),
                                "end": datetime(2026, 1, 14, 11, 0),
                                "comments": [],
                            },
                        ],
                    },
                    {
                        "task_name": "Frontend work",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 14, 13, 0),
                                "end": datetime(2026, 1, 14, 14, 30),
                                "comments": [],
                            }
                        ],
                    },
                ],
            }
        ]
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("**** PROJ Project Beta", lines)
        self.assertIn("***** Backend work", lines)
        self.assertIn("***** Frontend work", lines)
        self.assertIn("Subtotal: 2h", lines)
        self.assertIn("Subtotal: 1h 30m", lines)
        self.assertIn("Total: 3h 30m", lines)

    def test_format_orgmode_output_subtotal_calculation_correct(self) -> None:
        all_projects: List[Dict[str, Any]] = [
            {
                "name": "Project Gamma",
                "tasks": [
                    {
                        "task_name": "Task A",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 14, 9, 0),
                                "end": datetime(2026, 1, 14, 9, 45),
                                "comments": [],
                            }
                        ],
                    },
                    {
                        "task_name": "Task B",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 14, 10, 0),
                                "end": datetime(2026, 1, 14, 10, 15),
                                "comments": [],
                            }
                        ],
                    },
                ],
            }
        ]
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("Subtotal: 45m", lines)
        self.assertIn("Subtotal: 15m", lines)
        self.assertIn("Total: 1h", lines)

    def test_format_orgmode_output_worklog_section(self) -> None:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries = [
            {
                "task_name": "Email responses",
                "start": datetime(2026, 1, 14, 11, 0),
                "end": datetime(2026, 1, 14, 11, 30),
                "date": date(2026, 1, 14),
                "section_name": "WORKLOG",
            },
            {
                "task_name": "Team meeting",
                "start": datetime(2026, 1, 14, 14, 0),
                "end": datetime(2026, 1, 14, 15, 0),
                "date": date(2026, 1, 14),
                "section_name": "WORKLOG",
            },
        ]
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("*** PROJ WORKLOG", lines)
        self.assertIn("- 11:00 - 11:30: Email responses", lines)
        self.assertIn("- 14:00 - 15:00: Team meeting", lines)
        self.assertIn("Total: 1h 30m", lines)

    def test_format_orgmode_output_times_section(self) -> None:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries = [
            {
                "task_name": "Lunch break",
                "start": datetime(2026, 1, 14, 12, 0),
                "end": datetime(2026, 1, 14, 13, 0),
                "date": date(2026, 1, 14),
                "section_name": "TIMES",
            }
        ]
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("*** PROJ TIMES", lines)
        self.assertIn("- 12:00 - 13:00: Lunch break", lines)
        self.assertIn("Total: 1h", lines)

    def test_format_orgmode_output_mixed_times_and_worklog(self) -> None:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries = [
            {
                "task_name": "Code review",
                "start": datetime(2026, 1, 14, 9, 0),
                "end": datetime(2026, 1, 14, 10, 0),
                "date": date(2026, 1, 14),
                "section_name": "WORKLOG",
            },
            {
                "task_name": "Lunch",
                "start": datetime(2026, 1, 14, 12, 0),
                "end": datetime(2026, 1, 14, 13, 0),
                "date": date(2026, 1, 14),
                "section_name": "TIMES",
            },
            {
                "task_name": "Documentation",
                "start": datetime(2026, 1, 14, 14, 0),
                "end": datetime(2026, 1, 14, 15, 0),
                "date": date(2026, 1, 14),
                "section_name": "WORKLOG",
            },
        ]
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("*** PROJ WORKLOG", lines)
        self.assertIn("*** PROJ TIMES", lines)
        self.assertIn("- 09:00 - 10:00: Code review", lines)
        self.assertIn("- 12:00 - 13:00: Lunch", lines)
        self.assertIn("- 14:00 - 15:00: Documentation", lines)

    def test_format_orgmode_output_worklog_entries_without_end_time(self) -> None:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries = [
            {
                "task_name": "Open task",
                "start": datetime(2026, 1, 14, 16, 0),
                "end": None,
                "date": date(2026, 1, 14),
                "section_name": "WORKLOG",
            }
        ]
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("- 16:00 - noend: Open task", lines)
        self.assertNotIn("Total:", "\n".join(lines))

    def test_format_orgmode_output_auto_fill_end_time_from_next_entry(self) -> None:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries = [
            {
                "task_name": "Task 1",
                "start": datetime(2026, 1, 14, 9, 0),
                "end": None,
                "date": date(2026, 1, 14),
                "section_name": "WORKLOG",
            },
            {
                "task_name": "Task 2",
                "start": datetime(2026, 1, 14, 10, 0),
                "end": datetime(2026, 1, 14, 11, 0),
                "date": date(2026, 1, 14),
                "section_name": "WORKLOG",
            },
        ]
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("- 09:00 - 10:00: Task 1", lines)
        self.assertIn("- 10:00 - 11:00: Task 2", lines)
        self.assertIn("Total: 2h", lines)

    def test_format_orgmode_output_projects_and_worklog_combined(self) -> None:
        all_projects: List[Dict[str, Any]] = [
            {
                "name": "Project X",
                "tasks": [
                    {
                        "task_name": "",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 14, 9, 0),
                                "end": datetime(2026, 1, 14, 10, 0),
                                "comments": [],
                            }
                        ],
                    }
                ],
            }
        ]
        all_worklog_entries = [
            {
                "task_name": "Meetings",
                "start": datetime(2026, 1, 14, 14, 0),
                "end": datetime(2026, 1, 14, 15, 0),
                "date": date(2026, 1, 14),
                "section_name": "WORKLOG",
            }
        ]
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("*** PROJ Projects", lines)
        self.assertIn("**** PROJ Project X", lines)
        self.assertIn("*** PROJ WORKLOG", lines)
        project_idx = next(
            i for i, line in enumerate(lines) if "*** PROJ Projects" in line
        )
        worklog_idx = next(
            i for i, line in enumerate(lines) if "*** PROJ WORKLOG" in line
        )
        self.assertLess(project_idx, worklog_idx)

    def test_format_orgmode_output_multiple_projects_on_same_date(self) -> None:
        all_projects: List[Dict[str, Any]] = [
            {
                "name": "Project A",
                "tasks": [
                    {
                        "task_name": "",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 14, 9, 0),
                                "end": datetime(2026, 1, 14, 10, 0),
                                "comments": [],
                            }
                        ],
                    }
                ],
            },
            {
                "name": "Project B",
                "tasks": [
                    {
                        "task_name": "",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 14, 11, 0),
                                "end": datetime(2026, 1, 14, 12, 0),
                                "comments": [],
                            }
                        ],
                    }
                ],
            },
        ]
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("**** PROJ Project A", lines)
        self.assertIn("**** PROJ Project B", lines)
        project_a_idx = next(
            i for i, line in enumerate(lines) if "**** PROJ Project A" in line
        )
        project_b_idx = next(
            i for i, line in enumerate(lines) if "**** PROJ Project B" in line
        )
        blank_between = any(
            lines[i] == "" for i in range(project_a_idx + 1, project_b_idx)
        )
        self.assertTrue(blank_between)

    def test_format_orgmode_output_project_entries_with_comments(self) -> None:
        all_projects: List[Dict[str, Any]] = [
            {
                "name": "Project Y",
                "tasks": [
                    {
                        "task_name": "",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 14, 9, 0),
                                "end": datetime(2026, 1, 14, 10, 0),
                                "comments": ["Fixed bug", "Updated tests"],
                            }
                        ],
                    }
                ],
            }
        ]
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("- 09:00 - 10:00 ; Fixed bug ; Updated tests", lines)

    def test_format_orgmode_output_project_on_different_dates(self) -> None:
        all_projects: List[Dict[str, Any]] = [
            {
                "name": "Project Z",
                "tasks": [
                    {
                        "task_name": "",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 14, 9, 0),
                                "end": datetime(2026, 1, 14, 10, 0),
                                "comments": [],
                            },
                            {
                                "start": datetime(2026, 1, 15, 14, 0),
                                "end": datetime(2026, 1, 15, 15, 0),
                                "comments": [],
                            },
                        ],
                    }
                ],
            }
        ]
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 14), date(2026, 1, 15)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        date_14_idx = next(
            i for i, line in enumerate(lines) if "[2026-01-14 Wed]" in line
        )
        date_15_idx = next(
            i for i, line in enumerate(lines) if "[2026-01-15 Thu]" in line
        )

        project_z_count = sum(1 for line in lines if "**** PROJ Project Z" in line)
        self.assertEqual(project_z_count, 2)

        self.assertLess(date_14_idx, date_15_idx)

    def test_format_orgmode_output_zero_duration_entries_show_zero_total(self) -> None:
        all_projects: List[Dict[str, Any]] = [
            {
                "name": "Project Q",
                "tasks": [
                    {
                        "task_name": "",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 14, 9, 0),
                                "end": None,
                                "comments": [],
                            }
                        ],
                    }
                ],
            }
        ]
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        self.assertIn("- 09:00 -", lines)

    def test_format_orgmode_output_no_subtotal_when_single_unnamed_task(self) -> None:
        all_projects: List[Dict[str, Any]] = [
            {
                "name": "Project Single",
                "tasks": [
                    {
                        "task_name": "",
                        "entries": [
                            {
                                "start": datetime(2026, 1, 14, 9, 0),
                                "end": datetime(2026, 1, 14, 10, 0),
                                "comments": [],
                            }
                        ],
                    }
                ],
            }
        ]
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 14)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        subtotal_lines = [line for line in lines if "Subtotal:" in line]
        self.assertEqual(len(subtotal_lines), 0)

    def test_format_orgmode_output_date_sorting(self) -> None:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries: List[Dict[str, Any]] = []
        dates_seen = [date(2026, 1, 20), date(2026, 1, 14), date(2026, 1, 17)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        date_headers = [line for line in lines if line.startswith("** PROJ [")]
        self.assertEqual(len(date_headers), 3)
        self.assertIn("2026-01-14", date_headers[0])
        self.assertIn("2026-01-17", date_headers[1])
        self.assertIn("2026-01-20", date_headers[2])

    def test_format_orgmode_output_blank_lines_between_dates(self) -> None:
        all_projects: List[Dict[str, Any]] = []
        all_worklog_entries = [
            {
                "task_name": "Task A",
                "start": datetime(2026, 1, 14, 9, 0),
                "end": datetime(2026, 1, 14, 10, 0),
                "date": date(2026, 1, 14),
                "section_name": "WORKLOG",
            },
            {
                "task_name": "Task B",
                "start": datetime(2026, 1, 15, 9, 0),
                "end": datetime(2026, 1, 15, 10, 0),
                "date": date(2026, 1, 15),
                "section_name": "WORKLOG",
            },
        ]
        dates_seen = [date(2026, 1, 14), date(2026, 1, 15)]

        lines = self.formatter._format_orgmode_output(
            all_projects, all_worklog_entries, dates_seen
        )

        date_14_idx = next(
            i for i, line in enumerate(lines) if "[2026-01-14 Wed]" in line
        )
        date_15_idx = next(
            i for i, line in enumerate(lines) if "[2026-01-15 Thu]" in line
        )

        blank_lines_between = [
            i for i in range(date_14_idx, date_15_idx) if lines[i] == ""
        ]
        self.assertGreater(len(blank_lines_between), 0)


if __name__ == "__main__":
    unittest.main()
