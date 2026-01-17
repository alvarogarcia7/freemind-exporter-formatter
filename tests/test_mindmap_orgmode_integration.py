import unittest
import xml.etree.ElementTree as xml
from datetime import datetime, date

from mindmap_orgmode import Formatter


class TestMindmapOrgmodeIntegration(unittest.TestCase):

    def get_output_lines(self, root: xml.Element) -> list[str]:
        """Parse the root and return formatted output lines."""
        formatter = Formatter()
        formatter.parse(root)
        return formatter.format()

    def get_output(self, root: xml.Element) -> str:
        """Parse the root and return formatted output as a string."""
        return '\n'.join(self.get_output_lines(root))

    def test_end_to_end_project_with_subtasks(self) -> None:
        """E2E test: Read XML -> Extract data -> Format -> Print with projects and subtasks."""
        xml_str = """
        <node TEXT="Root">
            <node TEXT="18/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-18T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Main Project">
                        <node TEXT="Subtask 1">
                            <node TEXT="18/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-18T09:00+0400|datetime">
                                <node TEXT="18/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-18T10:00+0400|datetime"/>
                            </node>
                        </node>
                        <node TEXT="Subtask 2">
                            <node TEXT="18/01/2026 11:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-18T11:00+0400|datetime">
                                <node TEXT="18/01/2026 12:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-18T12:00+0400|datetime"/>
                            </node>
                        </node>
                    </node>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        self.assertIn("* PROJ Worklog", output)
        self.assertIn("**** PROJ Main Project", output)
        self.assertIn("***** Subtask 1", output)
        self.assertIn("- 09:00 - 10:00", output)
        self.assertIn("***** Subtask 2", output)
        self.assertIn("- 11:00 - 12:00", output)

    def test_simple_project_with_icons(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="16/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Simple Task">
                        <icon BUILTIN="bookmark"/>
                        <icon BUILTIN="stop-sign"/>
                        <node TEXT="16/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T09:00+0400|datetime">
                            <node TEXT="16/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-16T10:00+0400|datetime"/>
                        </node>
                    </node>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        self.assertIn("* PROJ Worklog", output)
        self.assertIn("** PROJ [2026-01-16 Fri]", output)
        self.assertIn("*** PROJ Projects", output)
        self.assertIn("**** PROJ Simple Task :Bookmark:StopSign:", output)
        self.assertIn("- 09:00 - 10:00", output)

    def test_simple_project_with_single_task(self) -> None:
        xml_str = """
        <node TEXT="Root">
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
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        self.assertIn("* PROJ Worklog", output)
        self.assertIn("** PROJ [2026-01-16 Fri]", output)
        self.assertIn("*** PROJ Projects", output)
        self.assertIn("**** PROJ Simple Task", output)
        self.assertIn("- 09:00 - 10:00", output)

    def test_tasks_with_comments(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Project with comments">
                        <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
                            <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime">
                                <node TEXT="Important comment"/>
                                <node TEXT="Another note"/>
                            </node>
                        </node>
                    </node>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        self.assertIn("- 08:36 - 11:16 ; Important comment ; Another note", output)

    def test_multiple_dates_sorted(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="22/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-22T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Task C">
                        <node TEXT="22/01/2026 14:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-22T14:00+0400|datetime">
                            <node TEXT="22/01/2026 15:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-22T15:00+0400|datetime"/>
                        </node>
                    </node>
                </node>
            </node>
            <node TEXT="20/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-20T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Task A">
                        <node TEXT="20/01/2026 09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-20T09:00+0400|datetime">
                            <node TEXT="20/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-20T10:00+0400|datetime"/>
                        </node>
                    </node>
                </node>
            </node>
            <node TEXT="21/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-21T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Task B">
                        <node TEXT="21/01/2026 11:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-21T11:00+0400|datetime">
                            <node TEXT="21/01/2026 12:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-21T12:00+0400|datetime"/>
                        </node>
                    </node>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        lines = output.split('\n')
        date_lines = [line for line in lines if line.startswith('** PROJ [')]
        self.assertEqual(len(date_lines), 3)
        self.assertIn('[2026-01-20 Tue]', date_lines[0])
        self.assertIn('[2026-01-21 Wed]', date_lines[1])
        self.assertIn('[2026-01-22 Thu]', date_lines[2])

    def test_empty_worklog(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="19/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-19T00:00+0400|date">
                <node TEXT="WORKLOG"/>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        self.assertIn("* PROJ Worklog", output)
        self.assertIn("** PROJ [2026-01-19 Mon]", output)
        self.assertNotIn("*** PROJ Projects", output)
        self.assertNotIn("*** PROJ WORKLOG", output)

    def test_git_annex_project_name_formatting(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="18/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-18T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="investigate git-annex">
                        <node TEXT="18/01/2026 08:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-18T08:00+0400|datetime">
                            <node TEXT="18/01/2026 10:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-18T10:00+0400|datetime"/>
                        </node>
                    </node>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        self.assertIn("**** PROJ investigate git-annex", output)

    def test_tasks_without_end_time_filled_by_next_task(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="17/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-17T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="17/01/2026 08:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-17T08:00+0400|datetime">
                        <node TEXT="First task"/>
                    </node>
                    <node TEXT="17/01/2026 09:30" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-17T09:30+0400|datetime">
                        <node TEXT="Second task"/>
                    </node>
                    <node TEXT="17/01/2026 14:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-17T14:00+0400|datetime">
                        <node TEXT="Third task"/>
                    </node>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        self.assertIn("- 08:00 - 09:30: First task", output)
        self.assertIn("- 09:30 - 14:00: Second task", output)
        self.assertIn("- 14:00 - noend: Third task", output)

    def test_mixed_projects_and_worklog_entries(self) -> None:
        xml_str = """
        <node TEXT="Root">
            <node TEXT="14/01/2026" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Investigate git-annex">
                        <node TEXT="14/01/2026 08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
                            <node TEXT="14/01/2026 11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime"/>
                        </node>
                    </node>
                    <node TEXT="14/01/2026 11:14" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:14+0400|datetime">
                        <node TEXT="Work on this"/>
                    </node>
                    <node TEXT="14/01/2026 11:21" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:21+0400|datetime">
                        <node TEXT="Work on that"/>
                    </node>
                </node>
            </node>
        </node>
        """
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        self.assertIn("*** PROJ Projects", output)
        self.assertIn("**** PROJ Investigate git-annex", output)
        self.assertIn("- 08:36 - 11:16", output)
        self.assertIn("*** PROJ WORKLOG", output)
        self.assertIn("- 11:14 - 11:21: Work on this", output)
        self.assertIn("- 11:21 - noend: Work on that", output)


if __name__ == '__main__':
    unittest.main()
