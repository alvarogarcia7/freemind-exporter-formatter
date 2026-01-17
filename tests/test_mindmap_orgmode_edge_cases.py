import unittest
import xml.etree.ElementTree as xml
from datetime import datetime, date

from mindmap_orgmode import Formatter


class TestMindmapOrgmodeEdgeCases(unittest.TestCase):

    def setUp(self) -> None:
        self.formatter = Formatter()

    def get_output_lines(self, root: xml.Element) -> list[str]:
        """Parse the root and return formatted output lines."""
        formatter = Formatter()
        formatter.parse(root)
        return formatter.format()

    def get_output(self, root: xml.Element) -> str:
        """Parse the root and return formatted output as a string."""
        return '\n'.join(self.get_output_lines(root))

    def test_node_without_date_object(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="Not a date node">
                <node TEXT="WORKLOG"/>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        date_nodes = self.formatter._find_all_date_nodes(root)
        self.assertEqual(len(date_nodes), 0)

    def test_deeply_nested_date_nodes(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="Level 1">
                <node TEXT="Level 2">
                    <node TEXT="Level 3">
                        <node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date">
                            <node TEXT="WORKLOG"/>
                        </node>
                    </node>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        date_nodes = self.formatter._find_all_date_nodes(root)
        self.assertEqual(len(date_nodes), 1)

    def test_date_node_without_worklog_child(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date">
                <node TEXT="TODO">
                    <node TEXT="Some task"/>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        self.assertIn("* PROJ Worklog", output)
        self.assertIn("** PROJ [2026-01-14 Wed]", output)
        self.assertNotIn("*** PROJ Projects", output)

    def test_worklog_with_only_non_time_nodes(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Just a text node"/>
                    <node TEXT="Another text node"/>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        self.assertIn("** PROJ [2026-01-14 Wed]", output)

    def test_malformed_datetime_attribute(self) -> None:
        xml_str = '<node TEXT="Invalid" OBJECT="org.freeplane.features.format.FormattedDate|not-a-date|datetime"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._parse_datetime_from_node(node)
        self.assertIsNone(result)

    def test_datetime_without_timezone(self) -> None:
        xml_str = '<node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36|datetime"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._parse_datetime_from_node(node)
        self.assertIsNotNone(result)
        self.assertEqual(result, datetime(2026, 1, 14, 8, 36))

    def test_task_node_with_no_children(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Empty task"/>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        self.assertIn("** PROJ [2026-01-14 Wed]", output)

    def test_project_with_empty_task_name(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="">
                        <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
                            <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime"/>
                        </node>
                    </node>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        self.assertIn("- 08:36 - 11:16", output)

    def test_multiple_comments_on_same_time_entry(self) -> None:
        xml_str = """
        <node TEXT="Start">
            <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime">
                <node TEXT="Comment 1"/>
                <node TEXT="Comment 2"/>
                <node TEXT="Comment 3"/>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_comments(node)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, ["Comment 1", "Comment 2", "Comment 3"])

    def test_task_with_only_start_time_no_description(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="14/01/2026 11:14" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:14+0400|datetime"/>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        self.assertIn("*** PROJ WORKLOG", output)

    def test_extract_data_with_duplicate_dates(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Task 1">
                        <node TEXT="14/01/2026 08:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:00+0400|datetime">
                            <node TEXT="14/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T09:00+0400|datetime"/>
                        </node>
                    </node>
                </node>
            </node>
            <node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Task 2">
                        <node TEXT="14/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T10:00+0400|datetime">
                            <node TEXT="14/01/2026 11:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:00+0400|datetime"/>
                        </node>
                    </node>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        date_nodes = self.formatter._find_all_date_nodes(root)
        all_projects, all_worklog_entries, dates_seen = self.formatter._extract_all_data(date_nodes)

        self.assertEqual(len(dates_seen), 1)
        self.assertEqual(len(all_projects), 2)

    def test_worklog_entry_sorting_by_start_time(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="14/01/2026 14:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T14:00+0400|datetime">
                        <node TEXT="Task C"/>
                    </node>
                    <node TEXT="14/01/2026 08:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:00+0400|datetime">
                        <node TEXT="Task A"/>
                    </node>
                    <node TEXT="14/01/2026 11:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:00+0400|datetime">
                        <node TEXT="Task B"/>
                    </node>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        lines = output.split('\n')
        worklog_lines = [line for line in lines if line.startswith('- ') and ':' in line]

        self.assertTrue(len(worklog_lines) >= 3)
        self.assertIn("08:00", worklog_lines[0])
        self.assertIn("11:00", worklog_lines[1])
        self.assertIn("14:00", worklog_lines[2])

    def test_time_entry_without_comments(self) -> None:
        entry = {
            'start': datetime(2026, 1, 14, 8, 36),
            'end': datetime(2026, 1, 14, 11, 16),
            'comments': []
        }
        result = self.formatter._format_time_entry(entry)
        self.assertEqual(result, "08:36 - 11:16")
        self.assertNotIn(';', result)

    def test_node_with_missing_object_attribute(self) -> None:
        xml_str = '<node TEXT="Some node"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._is_datetime_node(node)
        self.assertFalse(result)

    def test_node_with_empty_object_attribute(self) -> None:
        xml_str = '<node TEXT="Some node" OBJECT=""/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._is_datetime_node(node)
        self.assertFalse(result)

    def test_date_parsing_with_different_separators(self) -> None:
        xml_str = '<node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._get_date_from_node(node)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.year, 2026)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 14)


if __name__ == '__main__':
    unittest.main()
