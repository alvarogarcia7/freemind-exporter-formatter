from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml
from typing import List


class Formatter(MindmapExporter):
    def export(self, tree: xml.Element) -> None:
        output_lines = self._format_tree(tree)
        self._print_output(output_lines)

    def _format_tree(self, root: xml.Element) -> List[str]:
        return self._format_tree_as_titles(root, 1)

    def _format_tree_as_titles(self, root: xml.Element, level: int) -> List[str]:
        lines: List[str] = []
        
        if 'TEXT' not in root.attrib:
            for child in root:
                lines.extend(self._format_tree_as_titles(child, level))
            return lines

        lines.append(("#" * level) + " " + root.attrib['TEXT'])
        for child in root:
            if child.tag == 'node':
                lines.extend(self._format_tree_as_titles(child, level + 1))

        return lines

    def _print_output(self, lines: List[str]) -> None:
        for line in lines:
            print(line)
