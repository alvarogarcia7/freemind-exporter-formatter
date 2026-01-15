import unittest
import xml.etree.ElementTree as xml
import json as json_module
from datetime import datetime
from io import StringIO
import sys
from typing import Any, Dict

from json_formatter import Formatter


class TestJsonFormatter(unittest.TestCase):

    def setUp(self) -> None:
        self.formatter = Formatter()
        self.original_stdout = sys.stdout
        self.captured_output = StringIO()

    def tearDown(self) -> None:
        sys.stdout = self.original_stdout

    def capture_output(self) -> None:
        sys.stdout = self.captured_output

    def get_output(self) -> str:
        sys.stdout = self.original_stdout
        return self.captured_output.getvalue()

    def get_json_output(self) -> Dict[str, Any]:
        output = self.get_output()
        result: Dict[str, Any] = json_module.loads(output)
        return result

    def test_convert_simple_node_to_dict(self) -> None:
        xml_str = '<node TEXT="Simple Node" ID="ID_123" CREATED="1234567890"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._convert_node_to_dict(node)
        
        self.assertEqual(result['tag'], 'node')
        self.assertEqual(result['text'], 'Simple Node')
        self.assertEqual(result['attributes']['ID'], 'ID_123')
        self.assertEqual(result['attributes']['CREATED'], '1234567890')

    def test_convert_node_with_children(self) -> None:
        xml_str = """
        <node TEXT="Parent">
            <node TEXT="Child1"/>
            <node TEXT="Child2"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._convert_node_to_dict(node)
        
        self.assertEqual(result['text'], 'Parent')
        self.assertIn('children', result)
        self.assertEqual(len(result['children']), 2)
        self.assertEqual(result['children'][0]['text'], 'Child1')
        self.assertEqual(result['children'][1]['text'], 'Child2')

    def test_convert_node_without_children(self) -> None:
        xml_str = '<node TEXT="Leaf Node"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._convert_node_to_dict(node)
        
        self.assertNotIn('children', result)

    def test_parse_date_object_attribute(self) -> None:
        object_str = "org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date"
        result = self.formatter._parse_object_attribute(object_str)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['type'], 'org.freeplane.features.format.FormattedDate')
        self.assertEqual(result['value'], '2026-01-16T00:00+0400')
        self.assertEqual(result['format'], 'date')
        self.assertEqual(result['parsed_date'], '2026-01-16')

    def test_parse_datetime_object_attribute(self) -> None:
        object_str = "org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime"
        result = self.formatter._parse_object_attribute(object_str)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['type'], 'org.freeplane.features.format.FormattedDate')
        self.assertEqual(result['value'], '2026-01-16T09:00+0400')
        self.assertEqual(result['format'], 'datetime')
        self.assertEqual(result['parsed_datetime'], '2026-01-16T09:00:00')

    def test_parse_object_attribute_without_formatted_date(self) -> None:
        object_str = "some.other.object|value|type"
        result = self.formatter._parse_object_attribute(object_str)
        
        self.assertIsNone(result)

    def test_parse_object_attribute_malformed(self) -> None:
        object_str = "org.freeplane.features.format.FormattedDate|incomplete"
        result = self.formatter._parse_object_attribute(object_str)
        
        self.assertIsNone(result)

    def test_parse_datetime_with_timezone_plus(self) -> None:
        object_str = "org.freeplane.features.format.FormattedDate|2026-01-16T09:30+0400|datetime"
        result = self.formatter._parse_object_attribute(object_str)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['parsed_datetime'], '2026-01-16T09:30:00')

    def test_parse_datetime_with_timezone_minus(self) -> None:
        object_str = "org.freeplane.features.format.FormattedDate|2026-01-16T09:30-0500|datetime"
        result = self.formatter._parse_object_attribute(object_str)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['parsed_datetime'], '2026-01-16T09:30:00')

    def test_parse_datetime_without_timezone(self) -> None:
        object_str = "org.freeplane.features.format.FormattedDate|2026-01-16T09:30|datetime"
        result = self.formatter._parse_object_attribute(object_str)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['parsed_datetime'], '2026-01-16T09:30:00')

    def test_parse_invalid_date(self) -> None:
        object_str = "org.freeplane.features.format.FormattedDate|invalid-date|date"
        result = self.formatter._parse_object_attribute(object_str)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertNotIn('parsed_date', result)

    def test_parse_invalid_datetime(self) -> None:
        object_str = "org.freeplane.features.format.FormattedDate|invalid-datetime|datetime"
        result = self.formatter._parse_object_attribute(object_str)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertNotIn('parsed_datetime', result)

    def test_get_date_from_node(self) -> None:
        xml_str = '<node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._get_date_from_node(node)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.year, 2026)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 16)

    def test_get_date_from_node_invalid(self) -> None:
        xml_str = '<node TEXT="Invalid" OBJECT="org.freeplane.features.format.FormattedDate|invalid|date"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._get_date_from_node(node)
        
        self.assertIsNone(result)

    def test_get_date_from_node_without_object(self) -> None:
        xml_str = '<node TEXT="No Date"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._get_date_from_node(node)
        
        self.assertIsNone(result)

    def test_is_datetime_node_true(self) -> None:
        xml_str = '<node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._is_datetime_node(node)
        
        self.assertTrue(result)

    def test_is_datetime_node_false_for_date(self) -> None:
        xml_str = '<node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._is_datetime_node(node)
        
        self.assertFalse(result)

    def test_is_datetime_node_false_for_regular_node(self) -> None:
        xml_str = '<node TEXT="Regular Node"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._is_datetime_node(node)
        
        self.assertFalse(result)

    def test_parse_datetime_from_node(self) -> None:
        xml_str = '<node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._parse_datetime_from_node(node)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result, datetime(2026, 1, 16, 9, 0))

    def test_parse_datetime_from_node_with_plus_timezone(self) -> None:
        xml_str = '<node TEXT="16/01/2026 14:30" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T14:30+0800|datetime"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._parse_datetime_from_node(node)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.hour, 14)
        self.assertEqual(result.minute, 30)

    def test_parse_datetime_from_node_with_minus_timezone(self) -> None:
        xml_str = '<node TEXT="16/01/2026 10:45" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:45-0500|datetime"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._parse_datetime_from_node(node)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.hour, 10)
        self.assertEqual(result.minute, 45)

    def test_parse_datetime_from_node_invalid(self) -> None:
        xml_str = '<node TEXT="Invalid" OBJECT="org.freeplane.features.format.FormattedDate|invalid|datetime"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._parse_datetime_from_node(node)
        
        self.assertIsNone(result)

    def test_extract_time_entry_with_start_and_end(self) -> None:
        xml_str = """
        <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
            <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_time_entry(node)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['start'], '2026-01-16T09:00:00')
        self.assertEqual(result['end'], '2026-01-16T10:00:00')

    def test_extract_time_entry_with_task_description(self) -> None:
        xml_str = """
        <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
            <node TEXT="Work on feature X"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_time_entry(node)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['start'], '2026-01-16T09:00:00')
        self.assertEqual(result['task'], 'Work on feature X')

    def test_extract_time_entry_with_comments(self) -> None:
        xml_str = """
        <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
            <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime">
                <node TEXT="Comment 1"/>
                <node TEXT="Comment 2"/>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_time_entry(node)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['comments'], ['Comment 1', 'Comment 2'])

    def test_extract_time_entry_without_start_time(self) -> None:
        xml_str = '<node TEXT="Just a task"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_time_entry(node)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['task'], 'Just a task')
        self.assertIsNone(result['start'])
        self.assertIsNone(result['end'])

    def test_extract_task_time_entries(self) -> None:
        xml_str = """
        <node TEXT="Task">
            <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime"/>
            </node>
            <node TEXT="16/01/2026 11:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T11:00+0400|datetime">
                <node TEXT="16/01/2026 12:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T12:00+0400|datetime"/>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_task_time_entries(node)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['start'], '2026-01-16T09:00:00')
        self.assertEqual(result[1]['start'], '2026-01-16T11:00:00')

    def test_extract_task_time_entries_empty(self) -> None:
        xml_str = """
        <node TEXT="Task">
            <node TEXT="No time entries"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_task_time_entries(node)
        
        self.assertEqual(len(result), 0)

    def test_extract_project_data_with_direct_times(self) -> None:
        xml_str = """
        <node TEXT="Project A">
            <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime"/>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_project_data(node, "Project A")
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['name'], 'Project A')
        self.assertEqual(len(result['tasks']), 1)
        self.assertEqual(result['tasks'][0]['name'], '')

    def test_extract_project_data_with_subtasks(self) -> None:
        xml_str = """
        <node TEXT="Project B">
            <node TEXT="Subtask 1">
                <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                    <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime"/>
                </node>
            </node>
            <node TEXT="Subtask 2">
                <node TEXT="16/01/2026 11:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T11:00+0400|datetime">
                    <node TEXT="16/01/2026 12:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T12:00+0400|datetime"/>
                </node>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_project_data(node, "Project B")
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['name'], 'Project B')
        self.assertEqual(len(result['tasks']), 2)
        self.assertEqual(result['tasks'][0]['name'], 'Subtask 1')
        self.assertEqual(result['tasks'][1]['name'], 'Subtask 2')

    def test_extract_project_data_with_no_times(self) -> None:
        xml_str = """
        <node TEXT="Project C">
            <node TEXT="No time data"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_project_data(node, "Project C")
        
        self.assertIsNone(result)

    def test_extract_worklog_section_with_projects(self) -> None:
        xml_str = """
        <node TEXT="WORKLOG">
            <node TEXT="Project X">
                <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                    <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime"/>
                </node>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_worklog_section(node)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['name'], 'WORKLOG')
        self.assertIn('projects', result)
        self.assertEqual(len(result['projects']), 1)
        self.assertEqual(result['projects'][0]['name'], 'Project X')

    def test_extract_worklog_section_with_direct_entries(self) -> None:
        xml_str = """
        <node TEXT="WORKLOG">
            <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                <node TEXT="Work task"/>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_worklog_section(node)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['name'], 'WORKLOG')
        self.assertIn('entries', result)
        self.assertEqual(len(result['entries']), 1)

    def test_extract_worklog_section_empty(self) -> None:
        xml_str = """
        <node TEXT="WORKLOG">
            <node TEXT="No time data"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_worklog_section(node)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['name'], 'WORKLOG')
        self.assertIn('entries', result)
        self.assertEqual(len(result['entries']), 1)
        self.assertEqual(result['entries'][0]['task'], 'No time data')

    def test_extract_worklog_from_node_with_date(self) -> None:
        xml_str = """
        <node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date">
            <node TEXT="WORKLOG">
                <node TEXT="Task">
                    <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                        <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime"/>
                    </node>
                </node>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_worklog_from_node(node)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result['date'], '2026-01-16T00:00:00')
        self.assertIn('sections', result)
        self.assertEqual(len(result['sections']), 1)

    def test_extract_worklog_from_node_without_date(self) -> None:
        xml_str = """
        <node TEXT="Not a date">
            <node TEXT="WORKLOG"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_worklog_from_node(node)
        
        self.assertIsNone(result)

    def test_extract_worklog_from_node_with_times_section(self) -> None:
        xml_str = """
        <node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date">
            <node TEXT="TIMES">
                <node TEXT="Task">
                    <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                        <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime"/>
                    </node>
                </node>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        result = self.formatter._extract_worklog_from_node(node)
        
        self.assertIsNotNone(result)
        assert result is not None
        self.assertIn('sections', result)
        self.assertEqual(result['sections'][0]['name'], 'TIMES')

    def test_export_simple_tree(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="Child1"/>
            <node TEXT="Child2"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        self.capture_output()
        self.formatter.export(node)
        
        result = self.get_json_output()
        self.assertEqual(result['text'], 'Root')
        self.assertEqual(len(result['children']), 2)

    def test_export_tree_with_dates(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Task">
                        <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                            <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime"/>
                        </node>
                    </node>
                </node>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        self.capture_output()
        self.formatter.export(node)
        
        result = self.get_json_output()
        self.assertEqual(result['text'], 'Root')
        self.assertEqual(len(result['children']), 1)
        
        date_node = result['children'][0]
        self.assertIn('worklog', date_node)
        self.assertEqual(date_node['worklog']['date'], '2026-01-16T00:00:00')

    def test_export_produces_valid_json(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="Child1" ID="ID_1"/>
            <node TEXT="Child2" ID="ID_2"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        self.capture_output()
        self.formatter.export(node)
        
        output = self.get_output()
        # Should not raise exception
        parsed = json_module.loads(output)
        self.assertIsInstance(parsed, dict)

    def test_export_preserves_all_attributes(self) -> None:
        xml_str = '<node TEXT="Test" ID="ID_123" CREATED="1234567890" MODIFIED="1234567891" POSITION="right"/>'
        node = xml.fromstring(xml_str)
        self.capture_output()
        self.formatter.export(node)
        
        result = self.get_json_output()
        attrs = result['attributes']
        self.assertEqual(attrs['TEXT'], 'Test')
        self.assertEqual(attrs['ID'], 'ID_123')
        self.assertEqual(attrs['CREATED'], '1234567890')
        self.assertEqual(attrs['MODIFIED'], '1234567891')
        self.assertEqual(attrs['POSITION'], 'right')

    def test_export_deeply_nested_tree(self) -> None:
        xml_str = """
        <node TEXT="Level1">
            <node TEXT="Level2">
                <node TEXT="Level3">
                    <node TEXT="Level4"/>
                </node>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        self.capture_output()
        self.formatter.export(node)
        
        result = self.get_json_output()
        self.assertEqual(result['text'], 'Level1')
        level2 = result['children'][0]
        self.assertEqual(level2['text'], 'Level2')
        level3 = level2['children'][0]
        self.assertEqual(level3['text'], 'Level3')
        level4 = level3['children'][0]
        self.assertEqual(level4['text'], 'Level4')

    def test_export_with_special_characters(self) -> None:
        xml_str = '<node TEXT="Test &amp; &quot;special&quot; &lt;chars&gt;"/>'
        node = xml.fromstring(xml_str)
        self.capture_output()
        self.formatter.export(node)
        
        result = self.get_json_output()
        self.assertEqual(result['text'], 'Test & "special" <chars>')

    def test_export_with_unicode_characters(self) -> None:
        xml_str = '<node TEXT="Unicode: 日本語 Ελληνικά العربية"/>'
        node = xml.fromstring(xml_str)
        self.capture_output()
        self.formatter.export(node)
        
        result = self.get_json_output()
        self.assertIn('日本語', result['text'])
        self.assertIn('Ελληνικά', result['text'])
        self.assertIn('العربية', result['text'])

    def test_json_output_is_indented(self) -> None:
        xml_str = '<node TEXT="Root"><node TEXT="Child"/></node>'
        node = xml.fromstring(xml_str)
        self.capture_output()
        self.formatter.export(node)
        
        output = self.get_output()
        # Check for indentation (should have newlines and spaces)
        self.assertIn('\n', output)
        self.assertIn('  ', output)


if __name__ == '__main__':
    unittest.main()
