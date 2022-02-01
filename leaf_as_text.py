from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml


class Formatter(MindmapExporter):
    def export(self, tree: xml.Element) -> None:
        self._print_tree(tree)

    def _print_tree(self, root: xml.Element) -> None:
        self._print_tree_as_titles(root, 1)

    def _print_tree_as_titles(self, root: xml.Element, level: int) -> None:
        if len(root) != 0:
            print(("#" * level) + " " + root.attrib['TEXT'])
            for child in root:
                self._print_tree_as_titles(child, level + 1)
        else:
            print(root.attrib['TEXT'])
            print("") # In case there are two paragraphs together, needs a newline (otherwise it's the same paragraph)
