from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml


class Formatter(MindmapExporter):
    def parse(self, tree: xml.Element) -> None:
        self.lines = self._format_tree_as_titles(tree, 1)

    def format(self) -> list[str]:
        return self.lines.copy()

    def _format_tree_as_titles(self, root: xml.Element, level: int) -> list[str]:
        lines: list[str] = []

        if 'TEXT' not in root.attrib:
            for child in root:
                lines.extend(self._format_tree_as_titles(child, level))
            return lines

        node_children = [child for child in root if child.tag == 'node']

        if len(node_children) != 0:
            lines.append(("#" * level) + " " + root.attrib['TEXT'])
            for child in node_children:
                lines.extend(self._format_tree_as_titles(child, level + 1))
        else:
            lines.append(root.attrib['TEXT'])
            lines.append("")

        return lines
