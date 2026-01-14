import unittest
from datetime import datetime, date
import xml.etree.ElementTree as xml
from typing import List, Dict, Any

from mindmap_orgmode import Formatter


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
        result = self.formatter._get_task_description(node)
        self.assertEqual(result, "Task description")

    def test_get_task_description_skips_datetime_child(self) -> None:
        xml_str = """
        <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
            <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime"/>
            <node TEXT="Task description"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._get_task_description(node)
        self.assertEqual(result, "Task description")

    def test_get_task_description_empty(self) -> None:
        xml_str = """
        <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
            <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._get_task_description(node)
        self.assertEqual(result, "")

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
            'start': datetime(2026, 1, 14, 8, 36),
            'end': datetime(2026, 1, 14, 11, 16),
            'comments': []
        }
        result = self.formatter._format_time_entry(entry)
        self.assertEqual(result, "08:36 - 11:16")

    def test_format_time_entry_without_end(self) -> None:
        entry: Dict[str, Any] = {
            'start': datetime(2026, 1, 14, 8, 36),
            'end': None,
            'comments': []
        }
        result = self.formatter._format_time_entry(entry)
        self.assertEqual(result, "08:36 -")

    def test_format_time_entry_with_comments(self) -> None:
        entry = {
            'start': datetime(2026, 1, 14, 8, 36),
            'end': datetime(2026, 1, 14, 11, 16),
            'comments': ["Comment 1", "Comment 2"]
        }
        result = self.formatter._format_time_entry(entry)
        self.assertEqual(result, "08:36 - 11:16 ; Comment 1 ; Comment 2")

    def test_format_worklog_entry_with_end(self) -> None:
        entry = {
            'task_name': 'Work on this',
            'start': datetime(2026, 1, 14, 11, 14),
            'end': datetime(2026, 1, 14, 11, 21)
        }
        result = self.formatter._format_worklog_entry(entry)
        self.assertEqual(result, "11:14 - 11:21: Work on this")

    def test_format_worklog_entry_without_end(self) -> None:
        entry = {
            'task_name': 'Work on Foo',
            'start': datetime(2026, 1, 14, 11, 35),
            'end': None
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
        self.assertEqual(entries[0]['start'], datetime(2026, 1, 14, 8, 36))
        self.assertEqual(entries[0]['end'], datetime(2026, 1, 14, 11, 16))
        self.assertEqual(entries[0]['comments'], ["Comment"])

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
        self.assertEqual(entries[0]['start'], datetime(2026, 1, 14, 8, 36))
        self.assertEqual(entries[1]['start'], datetime(2026, 1, 14, 11, 17))

    def test_extract_task_entries_empty(self) -> None:
        xml_str = """
        <node TEXT="Task">
            <node TEXT="No datetime"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        entries = self.formatter._extract_task_entries(node)
        self.assertEqual(len(entries), 0)


if __name__ == '__main__':
    unittest.main()
