from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml


class Formatter(MindmapExporter):
    def export(self, tree: xml.Element) -> None:
        self._print_tree(tree)

    def _print_tree(self, root: xml.Element) -> None:
        self._print_tree_as_titles(root, 1)

    def _print_tree_as_titles(self, root: xml.Element, level: int) -> None:
        # Skip elements that don't have TEXT attribute (e.g., font, hook, edge elements)
        if 'TEXT' not in root.attrib:
            # Still process children of non-TEXT elements
            for child in root:
                self._print_tree_as_titles(child, level)
            return

        # Count node children only (skip non-node elements like font, hook, etc.)
        node_children = [child for child in root if child.tag == 'node']

        if len(node_children) != 0:
            print(("#" * level) + " " + root.attrib['TEXT'])
            for child in node_children:
                self._print_tree_as_titles(child, level + 1)
        else:
            print(root.attrib['TEXT'])
            print("") # In case there are two paragraphs together, needs a newline (otherwise it's the same paragraph)
