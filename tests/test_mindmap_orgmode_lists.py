import unittest
import xml.etree.ElementTree as xml
from io import StringIO
import sys

from mindmap_orgmode_lists import Formatter


class TestMindmapOrgmodeLists(unittest.TestCase):

    def setUp(self) -> None:
        self.formatter = Formatter()
        self.original_stdout = sys.stdout
        self.captured_output = StringIO()
        sys.stdout = self.captured_output

    def tearDown(self) -> None:
        sys.stdout = self.original_stdout

    def get_output(self) -> str:
        return self.captured_output.getvalue()

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

    def test_is_todo_with_todo_node_extra_spaces(self) -> None:
        xml_str = '<node TEXT="  ! Buy Milk  "/>'
        node = xml.fromstring(xml_str)
        self.assertTrue(self.formatter._is_todo(node))

    def test_is_todo_with_non_todo_node(self) -> None:
        xml_str = '<node TEXT="Regular Node"/>'
        node = xml.fromstring(xml_str)
        self.assertFalse(self.formatter._is_todo(node))

    def test_get_node_children(self) -> None:
        xml_str = '''<node TEXT="Parent">
            <node TEXT="Child1"/>
            <font SIZE="10"/>
            <node TEXT="Child2"/>
            <edge COLOR="red"/>
        </node>'''
        node = xml.fromstring(xml_str)
        children = self.formatter._get_node_children(node)
        self.assertEqual(len(children), 2)
        self.assertEqual(children[0].attrib['TEXT'], 'Child1')
        self.assertEqual(children[1].attrib['TEXT'], 'Child2')

    def test_simple_tree_with_leaf_and_parent(self) -> None:
        xml_str = '''<node TEXT="Root">
            <node TEXT="Leaf1"/>
            <node TEXT="Parent">
                <node TEXT="Child"/>
            </node>
        </node>'''
        root = xml.fromstring(xml_str)
        self.formatter.export(root)
        output = self.get_output()

        lines = output.split('\n')
        self.assertEqual(lines[0], '#+title: Export')
        self.assertEqual(lines[1], '')
        self.assertIn('* PROJ Root', output)
        self.assertIn('- Leaf1', output)
        self.assertIn('** PROJ Parent', output)
        self.assertIn('- Child', output)

    def test_leaf_nodes_printed_before_non_leaf(self) -> None:
        xml_str = '''<node TEXT="Root">
            <node TEXT="Leaf1"/>
            <node TEXT="Leaf2"/>
            <node TEXT="Parent">
                <node TEXT="Child"/>
            </node>
            <node TEXT="Leaf3"/>
        </node>'''
        root = xml.fromstring(xml_str)
        self.formatter.export(root)
        output = self.get_output()

        lines = output.split('\n')
        leaf1_idx = next(i for i, line in enumerate(lines) if '- Leaf1' in line)
        leaf2_idx = next(i for i, line in enumerate(lines) if '- Leaf2' in line)
        leaf3_idx = next(i for i, line in enumerate(lines) if '- Leaf3' in line)
        parent_idx = next(i for i, line in enumerate(lines) if '** PROJ Parent' in line)

        self.assertLess(leaf1_idx, parent_idx)
        self.assertLess(leaf2_idx, parent_idx)
        self.assertLess(leaf3_idx, parent_idx)

    def test_todo_nodes_printed_after_non_todo(self) -> None:
        xml_str = '''<node TEXT="Root">
            <node TEXT="Leaf1"/>
            <node TEXT="! TODO Item"/>
        </node>'''
        root = xml.fromstring(xml_str)
        self.formatter.export(root)
        output = self.get_output()

        lines = output.split('\n')
        leaf_idx = next(i for i, line in enumerate(lines) if '- Leaf1' in line)
        todo_idx = next(i for i, line in enumerate(lines) if '** TODO TODO Item' in line)

        self.assertLess(leaf_idx, todo_idx)

    def test_todo_leaf_node_becomes_heading(self) -> None:
        xml_str = '''<node TEXT="Root">
            <node TEXT="! Buy Milk"/>
        </node>'''
        root = xml.fromstring(xml_str)
        self.formatter.export(root)
        output = self.get_output()

        self.assertIn('** TODO Buy Milk', output)
        self.assertNotIn('- ! Buy Milk', output)

    def test_todo_non_leaf_node_becomes_heading(self) -> None:
        xml_str = '''<node TEXT="Root">
            <node TEXT="! Project">
                <node TEXT="Subtask"/>
            </node>
        </node>'''
        root = xml.fromstring(xml_str)
        self.formatter.export(root)
        output = self.get_output()

        self.assertIn('** TODO Project', output)
        self.assertNotIn('- ! Project', output)

    def test_todo_marker_removed_from_output(self) -> None:
        xml_str = '''<node TEXT="Root">
            <node TEXT="! Buy Groceries"/>
        </node>'''
        root = xml.fromstring(xml_str)
        self.formatter.export(root)
        output = self.get_output()

        self.assertIn('Buy Groceries', output)
        self.assertNotIn('! Buy Groceries', output)

    def test_nested_structure_with_proper_levels(self) -> None:
        xml_str = '''<node TEXT="Level1">
            <node TEXT="Level2">
                <node TEXT="Level3">
                    <node TEXT="Level4">
                        <node TEXT="Level5"/>
                    </node>
                </node>
            </node>
        </node>'''
        root = xml.fromstring(xml_str)
        self.formatter.export(root)
        output = self.get_output()

        self.assertIn('* PROJ Level1', output)
        self.assertIn('** PROJ Level2', output)
        self.assertIn('*** PROJ Level3', output)
        self.assertIn('**** PROJ Level4', output)
        self.assertIn('- Level5', output)

    def test_empty_text_attribute_handling(self) -> None:
        xml_str = '''<node TEXT="Root">
            <node>
                <node TEXT="Child"/>
            </node>
        </node>'''
        root = xml.fromstring(xml_str)
        self.formatter.export(root)
        output = self.get_output()

        # Should still process the child even though parent has no TEXT
        self.assertIn('- Child', output)

    def test_complex_tree_ordering(self) -> None:
        """Test the example from the requirement."""
        xml_str = '''<node TEXT="16/01/2026">
            <node TEXT="A0.1">
                <node TEXT="A1.1">
                    <node TEXT="A2.1">
                        <node TEXT="A3-Leaf"/>
                    </node>
                    <node TEXT="A2.2-Leaf"/>
                    <node TEXT="! Buy Groceries"/>
                </node>
                <node TEXT="A1.2-Leaf"/>
            </node>
            <node TEXT="B0.1-Leaf"/>
            <node TEXT="! Buy Milk"/>
        </node>'''
        root = xml.fromstring(xml_str)
        self.formatter.export(root)
        output = self.get_output()

        lines = output.strip().split('\n')

        # Verify header
        self.assertEqual(lines[0], '#+title: Export')
        self.assertEqual(lines[1], '')

        # Verify structure
        self.assertIn('* PROJ 16/01/2026', output)
        self.assertIn('- B0.1-Leaf', output)
        self.assertIn('** PROJ A0.1', output)
        self.assertIn('- A1.2-Leaf', output)
        self.assertIn('*** PROJ A1.1', output)
        self.assertIn('- A2.2-Leaf', output)
        self.assertIn('**** PROJ A2.1', output)
        self.assertIn('- A3-Leaf', output)
        self.assertIn('**** TODO Buy Groceries', output)
        self.assertIn('** TODO Buy Milk', output)

    def test_header_format(self) -> None:
        xml_str = '<node TEXT="Test"/>'
        root = xml.fromstring(xml_str)
        self.formatter.export(root)
        output = self.get_output()

        lines = output.split('\n')
        self.assertEqual(lines[0], '#+title: Export')
        self.assertEqual(lines[1], '')

    def test_single_leaf_node(self) -> None:
        xml_str = '''<node TEXT="Root">
            <node TEXT="Leaf"/>
        </node>'''
        root = xml.fromstring(xml_str)
        self.formatter.export(root)
        output = self.get_output()

        self.assertIn('* PROJ Root', output)
        self.assertIn('- Leaf', output)

    def test_single_todo_node(self) -> None:
        xml_str = '''<node TEXT="Root">
            <node TEXT="! TODO"/>
        </node>'''
        root = xml.fromstring(xml_str)
        self.formatter.export(root)
        output = self.get_output()

        self.assertIn('** TODO TODO', output)

    def test_root_node_never_todo(self) -> None:
        """Root node should always be PROJ, even if it starts with !"""
        xml_str = '<node TEXT="! Root"/>'
        root = xml.fromstring(xml_str)
        self.formatter.export(root)
        output = self.get_output()

        # Root should keep the ! in the text since we don't remove it for root
        self.assertIn('* PROJ ! Root', output)


if __name__ == '__main__':
    unittest.main()
