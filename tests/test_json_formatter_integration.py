import unittest
import xml.etree.ElementTree as xml
import json as json_module
from io import StringIO
import sys
from typing import Any, Dict

from json_formatter import Formatter


class TestJsonFormatterIntegration(unittest.TestCase):

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

    def test_simple_worklog_export(self) -> None:
        xml_str = """
        <node TEXT="Test Mindmap">
            <node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Simple Task">
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
        
        self.assertEqual(result['text'], 'Test Mindmap')
        self.assertEqual(len(result['children']), 1)
        
        date_node = result['children'][0]
        self.assertEqual(date_node['text'], '16/01/2026')
        self.assertIn('worklog', date_node)
        
        worklog = date_node['worklog']
        self.assertEqual(worklog['date'], '2026-01-16T00:00:00')
        self.assertEqual(len(worklog['sections']), 1)
        
        section = worklog['sections'][0]
        self.assertEqual(section['name'], 'WORKLOG')
        self.assertEqual(len(section['projects']), 1)
        
        project = section['projects'][0]
        self.assertEqual(project['name'], 'Simple Task')
        self.assertEqual(len(project['tasks']), 1)
        
        task = project['tasks'][0]
        self.assertEqual(len(task['entries']), 1)
        
        entry = task['entries'][0]
        self.assertEqual(entry['start'], '2026-01-16T09:00:00')
        self.assertEqual(entry['end'], '2026-01-16T10:00:00')

    def test_multiple_projects_export(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Project A">
                        <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                            <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime"/>
                        </node>
                    </node>
                    <node TEXT="Project B">
                        <node TEXT="16/01/2026 11:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T11:00+0400|datetime">
                            <node TEXT="16/01/2026 12:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T12:00+0400|datetime"/>
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
        worklog = result['children'][0]['worklog']
        section = worklog['sections'][0]
        
        self.assertEqual(len(section['projects']), 2)
        self.assertEqual(section['projects'][0]['name'], 'Project A')
        self.assertEqual(section['projects'][1]['name'], 'Project B')

    def test_project_with_subtasks_export(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Complex Project">
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
                </node>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        self.capture_output()
        self.formatter.export(node)
        
        result = self.get_json_output()
        project = result['children'][0]['worklog']['sections'][0]['projects'][0]
        
        self.assertEqual(project['name'], 'Complex Project')
        self.assertEqual(len(project['tasks']), 2)
        self.assertEqual(project['tasks'][0]['name'], 'Subtask 1')
        self.assertEqual(project['tasks'][1]['name'], 'Subtask 2')

    def test_direct_time_entries_export(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                        <node TEXT="Quick meeting"/>
                    </node>
                    <node TEXT="16/01/2026 11:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T11:00+0400|datetime">
                        <node TEXT="16/01/2026 12:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T12:00+0400|datetime"/>
                        <node TEXT="Lunch break"/>
                    </node>
                </node>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        self.capture_output()
        self.formatter.export(node)
        
        result = self.get_json_output()
        section = result['children'][0]['worklog']['sections'][0]
        
        self.assertIn('entries', section)
        self.assertEqual(len(section['entries']), 2)
        self.assertEqual(section['entries'][0]['task'], 'Quick meeting')
        self.assertEqual(section['entries'][1]['task'], 'Lunch break')

    def test_time_entry_with_comments_export(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Project">
                        <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                            <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime">
                                <node TEXT="Comment 1"/>
                                <node TEXT="Comment 2"/>
                            </node>
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
        entry = result['children'][0]['worklog']['sections'][0]['projects'][0]['tasks'][0]['entries'][0]
        
        self.assertIn('comments', entry)
        self.assertEqual(len(entry['comments']), 2)
        self.assertEqual(entry['comments'][0], 'Comment 1')
        self.assertEqual(entry['comments'][1], 'Comment 2')

    def test_multiple_dates_export(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Task 1">
                        <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                            <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime"/>
                        </node>
                    </node>
                </node>
            </node>
            <node TEXT="17/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-17T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Task 2">
                        <node TEXT="17/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-17T09:00+0400|datetime">
                            <node TEXT="17/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-17T10:00+0400|datetime"/>
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
        self.assertEqual(len(result['children']), 2)
        
        date1 = result['children'][0]
        self.assertEqual(date1['worklog']['date'], '2026-01-16T00:00:00')
        
        date2 = result['children'][1]
        self.assertEqual(date2['worklog']['date'], '2026-01-17T00:00:00')

    def test_times_section_export(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date">
                <node TEXT="TIMES">
                    <node TEXT="Meeting">
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
        section = result['children'][0]['worklog']['sections'][0]
        
        self.assertEqual(section['name'], 'TIMES')
        self.assertEqual(len(section['projects']), 1)

    def test_mixed_worklog_and_times_sections_export(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Project A">
                        <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                            <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime"/>
                        </node>
                    </node>
                </node>
                <node TEXT="TIMES">
                    <node TEXT="Project B">
                        <node TEXT="16/01/2026 11:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T11:00+0400|datetime">
                            <node TEXT="16/01/2026 12:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T12:00+0400|datetime"/>
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
        sections = result['children'][0]['worklog']['sections']
        
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0]['name'], 'WORKLOG')
        self.assertEqual(sections[1]['name'], 'TIMES')

    def test_hierarchical_mindmap_without_worklog_export(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="Branch 1">
                <node TEXT="Leaf 1.1"/>
                <node TEXT="Leaf 1.2"/>
            </node>
            <node TEXT="Branch 2">
                <node TEXT="Leaf 2.1"/>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        self.capture_output()
        self.formatter.export(node)
        
        result = self.get_json_output()
        
        self.assertEqual(result['text'], 'Root')
        self.assertEqual(len(result['children']), 2)
        self.assertEqual(result['children'][0]['text'], 'Branch 1')
        self.assertEqual(len(result['children'][0]['children']), 2)
        self.assertEqual(result['children'][1]['text'], 'Branch 2')
        self.assertEqual(len(result['children'][1]['children']), 1)

    def test_empty_worklog_section_export(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="No time entries"/>
                </node>
            </node>
        </node>
        """
        node = xml.fromstring(xml_str)
        self.capture_output()
        self.formatter.export(node)
        
        result = self.get_json_output()
        date_node = result['children'][0]
        
        # Worklog is included even with entries that have no time data
        self.assertIn('worklog', date_node)
        self.assertEqual(len(date_node['worklog']['sections'][0]['entries']), 1)

    def test_node_attributes_preserved_export(self) -> None:
        xml_str = """
        <node TEXT="Root" ID="ID_ROOT" CREATED="1234567890" MODIFIED="1234567891" POSITION="center">
            <node TEXT="Child" ID="ID_CHILD" CREATED="1234567892" MODIFIED="1234567893" STYLE="fork"/>
        </node>
        """
        node = xml.fromstring(xml_str)
        self.capture_output()
        self.formatter.export(node)
        
        result = self.get_json_output()
        
        root_attrs = result['attributes']
        self.assertEqual(root_attrs['TEXT'], 'Root')
        self.assertEqual(root_attrs['ID'], 'ID_ROOT')
        self.assertEqual(root_attrs['CREATED'], '1234567890')
        
        child_attrs = result['children'][0]['attributes']
        self.assertEqual(child_attrs['TEXT'], 'Child')
        self.assertEqual(child_attrs['ID'], 'ID_CHILD')
        self.assertEqual(child_attrs['STYLE'], 'fork')


if __name__ == '__main__':
    unittest.main()
