import unittest
import xml.etree.ElementTree as xml
from datetime import datetime, date

from orgmode_date_sections import Formatter


class TestOrgmodeDateSections(unittest.TestCase):
    def setUp(self) -> None:
        self.formatter = Formatter()

    def get_output_lines(self, root: xml.Element) -> list[str]:
        """Parse the root and return formatted output lines."""
        formatter = Formatter()
        formatter.parse(root)
        return formatter.format()

    def get_output(self, root: xml.Element) -> str:
        """Parse the root and return formatted output as a string."""
        return "\n".join(self.get_output_lines(root))

    # ========== Helper Method Tests ==========

    def test_is_leaf_with_leaf_node(self) -> None:
        xml_str = '<node TEXT="Leaf"/>'
        node = xml.fromstring(xml_str)
        self.assertTrue(self.formatter._is_leaf(node))

    def test_is_leaf_with_non_leaf_node(self) -> None:
        xml_str = '<node TEXT="Parent"><node TEXT="Child"/></node>'
        node = xml.fromstring(xml_str)
        self.assertFalse(self.formatter._is_leaf(node))

    def test_is_leaf_ignores_non_node_children(self) -> None:
        xml_str = '<node TEXT="Parent"><font SIZE="10"/><edge COLOR="red"/></node>'
        node = xml.fromstring(xml_str)
        self.assertTrue(self.formatter._is_leaf(node))

    def test_is_todo_with_todo_node(self) -> None:
        xml_str = '<node TEXT="! Buy Milk"/>'
        node = xml.fromstring(xml_str)
        self.assertTrue(self.formatter._is_todo(node))

    def test_is_todo_with_non_todo_node(self) -> None:
        xml_str = '<node TEXT="Regular Node"/>'
        node = xml.fromstring(xml_str)
        self.assertFalse(self.formatter._is_todo(node))

    def test_get_node_children(self) -> None:
        xml_str = """<node TEXT="Parent">
            <node TEXT="Child1"/>
            <font SIZE="10"/>
            <node TEXT="Child2"/>
        </node>"""
        node = xml.fromstring(xml_str)
        children = self.formatter._get_node_children(node)
        self.assertEqual(len(children), 2)
        self.assertEqual(children[0].attrib["TEXT"], "Child1")
        self.assertEqual(children[1].attrib["TEXT"], "Child2")

    def test_get_date_from_node(self) -> None:
        xml_str = '<node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._get_date_from_node(node)
        self.assertEqual(result, date(2026, 1, 24))

    def test_get_date_from_node_invalid(self) -> None:
        xml_str = '<node TEXT="Invalid"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._get_date_from_node(node)
        self.assertIsNone(result)

    def test_is_datetime_node_true(self) -> None:
        xml_str = '<node TEXT="08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime"/>'
        node = xml.fromstring(xml_str)
        self.assertTrue(self.formatter._is_datetime_node(node))

    def test_is_datetime_node_false(self) -> None:
        xml_str = '<node TEXT="Regular"/>'
        node = xml.fromstring(xml_str)
        self.assertFalse(self.formatter._is_datetime_node(node))

    def test_parse_datetime_from_node(self) -> None:
        xml_str = '<node TEXT="08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._parse_datetime_from_node(node)
        self.assertEqual(result, datetime(2026, 1, 14, 8, 36))

    def test_parse_datetime_from_node_invalid(self) -> None:
        xml_str = '<node TEXT="Invalid"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._parse_datetime_from_node(node)
        self.assertIsNone(result)

    def test_find_end_time(self) -> None:
        xml_str = """<node TEXT="08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
            <node TEXT="11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T11:16+0400|datetime"/>
        </node>"""
        node = xml.fromstring(xml_str)
        result = self.formatter._find_end_time(node)
        self.assertEqual(result, datetime(2026, 1, 14, 11, 16))

    def test_find_end_time_none(self) -> None:
        xml_str = '<node TEXT="08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime"/>'
        node = xml.fromstring(xml_str)
        result = self.formatter._find_end_time(node)
        self.assertIsNone(result)

    def test_get_task_description_simple(self) -> None:
        xml_str = """<node TEXT="08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
            <node TEXT="Description"/>
        </node>"""
        node = xml.fromstring(xml_str)
        desc, tags = self.formatter._get_task_description(node)
        self.assertEqual(desc, "Description")
        self.assertEqual(tags, [])

    def test_get_task_description_with_tags(self) -> None:
        xml_str = """<node TEXT="08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-14T08:36+0400|datetime">
            <icon BUILTIN="stop-sign"/>
            <node TEXT="Description"/>
        </node>"""
        node = xml.fromstring(xml_str)
        desc, tags = self.formatter._get_task_description(node)
        self.assertEqual(desc, "Description")
        self.assertEqual(tags, ["StopSign"])

    def test_extract_tags_from_node(self) -> None:
        xml_str = """<node TEXT="Task">
            <icon BUILTIN="bookmark"/>
            <icon BUILTIN="stop-sign"/>
        </node>"""
        node = xml.fromstring(xml_str)
        tags = self.formatter._extract_tags_from_node(node)
        self.assertEqual(tags, ["Bookmark", "StopSign"])

    # ========== Date Node Finding Tests ==========

    def test_find_all_date_nodes_single(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date"/>
        </node>"""
        root = xml.fromstring(xml_str)
        date_nodes = self.formatter._find_all_date_nodes(root)
        self.assertEqual(len(date_nodes), 1)

    def test_find_all_date_nodes_multiple(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date"/>
            <node TEXT="2026-01-25" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-25T00:00+0400|date"/>
        </node>"""
        root = xml.fromstring(xml_str)
        date_nodes = self.formatter._find_all_date_nodes(root)
        self.assertEqual(len(date_nodes), 2)

    def test_find_all_date_nodes_nested(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="Parent">
                <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date"/>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        date_nodes = self.formatter._find_all_date_nodes(root)
        self.assertEqual(len(date_nodes), 1)

    # ========== Section Processing Tests ==========

    def test_simple_date_with_worklog_section(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Task 1"/>
                    <node TEXT="Task 2"/>
                </node>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)

        self.assertIn("* [2026-01-24 Sat]", output)
        self.assertIn("** PROJ WORKLOG", output)
        self.assertIn("- Task 1", output)
        self.assertIn("- Task 2", output)

    def test_simple_date_with_times_section(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="TIMES">
                    <node TEXT="08:36" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T08:36+0400|datetime">
                        <node TEXT="11:16" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T11:16+0400|datetime"/>
                        <node TEXT="Work task"/>
                    </node>
                </node>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)

        self.assertIn("* [2026-01-24 Sat]", output)
        self.assertIn("** PROJ TIMES", output)
        self.assertIn("- 08:36 - 11:16: Work task", output)

    def test_todo_section_no_proj_prefix(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="TODO">
                    <node TEXT="! Buy Milk"/>
                </node>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)

        self.assertIn("* [2026-01-24 Sat]", output)
        self.assertIn("** TODO", output)
        self.assertNotIn("** PROJ TODO", output)

    def test_leaf_and_non_leaf_ordering(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Leaf1"/>
                    <node TEXT="NonLeaf1">
                        <node TEXT="Child1"/>
                    </node>
                    <node TEXT="Leaf2"/>
                </node>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        lines = output.split("\n")

        # Find indices
        leaf1_idx = next(i for i, line in enumerate(lines) if "- Leaf1" in line)
        leaf2_idx = next(i for i, line in enumerate(lines) if "- Leaf2" in line)
        # NonLeaf1 with only leaf children at level 0 should become a list item
        nonleaf_idx = next(i for i, line in enumerate(lines) if "- NonLeaf1" in line)

        # Leaves should come before non-leaves
        self.assertLess(leaf1_idx, nonleaf_idx)
        self.assertLess(leaf2_idx, nonleaf_idx)

    def test_nested_list_items_indentation(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Parent">
                        <node TEXT="Child1"/>
                        <node TEXT="Child2"/>
                    </node>
                </node>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        lines = output.split("\n")

        # Find lines with proper formatting
        # Parent with only leaf children at level 0 should be a list item
        has_parent = any("- Parent" in line for line in lines)
        has_child1 = any("  - Child1" in line for line in lines)
        has_child2 = any("  - Child2" in line for line in lines)

        self.assertTrue(has_parent, "Parent should be a list item")
        self.assertTrue(has_child1, "Child1 should be an indented list item")
        self.assertTrue(has_child2, "Child2 should be an indented list item")

    def test_todo_items_within_section(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="! Todo Item"/>
                    <node TEXT="Regular Item"/>
                </node>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)

        self.assertIn("*** TODO Todo Item", output)
        self.assertIn("- Regular Item", output)

    def test_multiple_sections_same_date(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="Task 1"/>
                </node>
                <node TEXT="LEARNLOG">
                    <node TEXT="Idea 1"/>
                </node>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)

        self.assertIn("** PROJ WORKLOG", output)
        self.assertIn("** PROJ LEARNLOG", output)
        self.assertIn("- Task 1", output)
        self.assertIn("- Idea 1", output)

    # ========== TIMES Section Tests ==========

    def test_times_with_tags(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="TIMES">
                    <node TEXT="18:46" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T18:46+0400|datetime">
                        <node TEXT="18:59" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T18:59+0400|datetime"/>
                        <icon BUILTIN="bookmark"/>
                        <node TEXT="Set up X1"/>
                    </node>
                </node>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)

        self.assertIn("- 18:46 - 18:59: Set up X1 :Bookmark:", output)

    def test_times_auto_fill_end_time(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="TIMES">
                    <node TEXT="08:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T08:00+0400|datetime">
                        <node TEXT="Task 1"/>
                    </node>
                    <node TEXT="09:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T09:00+0400|datetime">
                        <node TEXT="Task 2"/>
                    </node>
                </node>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        lines = output.split("\n")

        # First entry should have end time auto-filled from second entry's start time
        task1_line = next(line for line in lines if "Task 1" in line)
        self.assertIn("- 08:00 - 09:00: Task 1", task1_line)

    def test_times_without_end_time(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="TIMES">
                    <node TEXT="18:00" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T18:00+0400|datetime">
                        <node TEXT="Open task"/>
                    </node>
                </node>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)

        self.assertIn("- 18:00 - noend: Open task", output)

    # ========== Multiple Dates Tests ==========

    def test_multiple_dates_sorted(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-25" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-25T00:00+0400|date">
                <node TEXT="WORKLOG"><node TEXT="Task 2"/></node>
            </node>
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="WORKLOG"><node TEXT="Task 1"/></node>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)
        lines = output.split("\n")

        # Find indices
        date1_idx = next(i for i, line in enumerate(lines) if "2026-01-24" in line)
        date2_idx = next(i for i, line in enumerate(lines) if "2026-01-25" in line)

        self.assertLess(date1_idx, date2_idx, "Dates should be sorted chronologically")

    # ========== Edge Cases Tests ==========

    def test_empty_date_node(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date"/>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)

        # Should not crash, and date should not appear (no sections)
        self.assertNotIn("2026-01-24", output)

    def test_section_with_no_children(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="WORKLOG"/>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)

        self.assertIn("** PROJ WORKLOG", output)

    def test_deeply_nested_structure(self) -> None:
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="WORKLOG">
                    <node TEXT="L1">
                        <node TEXT="L2">
                            <node TEXT="L3">
                                <node TEXT="L4"/>
                            </node>
                        </node>
                    </node>
                </node>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)

        # Should not crash and should handle deep nesting
        self.assertIn("L1", output)
        self.assertIn("L2", output)
        self.assertIn("L3", output)
        self.assertIn("L4", output)

    def test_mixed_leaf_and_non_leaf_children(self) -> None:
        """Test RAYW-like mixed structure."""
        xml_str = """<node TEXT="Root">
            <node TEXT="2026-01-24" OBJECT="org.freeplane.features.format.FormattedDate|2026-01-24T00:00+0400|date">
                <node TEXT="RAYW">
                    <node TEXT="Direct Leaf"/>
                    <node TEXT="Header">
                        <node TEXT="Child Leaf"/>
                    </node>
                </node>
            </node>
        </node>"""
        root = xml.fromstring(xml_str)
        output = self.get_output(root)

        self.assertIn("- Direct Leaf", output)
        # In RAYW section, non-leaf items become headers without PROJ prefix
        self.assertIn("*** Header", output)
        self.assertIn("- Child Leaf", output)


if __name__ == "__main__":
    unittest.main()
