from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml


class Formatter(MindmapExporter):
    def export(self, tree: xml.Element) -> None:
        self._print_tree(tree)

    def _print_tree(self, root: xml.Element) -> None:
        self._print_tree_as_titles(root, 0)

    def _print_tree_as_titles(self, root: xml.Element, level: int) -> None:
        # Skip elements that don't have TEXT attribute (e.g., font, hook, edge elements)
        if 'TEXT' not in root.attrib:
            # Still process children of non-TEXT elements
            for child in root:
                self._print_tree_as_titles(child, level)
            return

        node_text = root.attrib['TEXT']
        if level == 1:
            print(f"""
\\section{{{node_text}}}
""")
        elif level == 2:
            print(f"""
\\begin{{frame}}
    \\frametitle{{{node_text}}}
""")
            print("\\begin{itemize}")

        elif level == 3:
            print(f"    \\item {node_text}")

        # Process only node children (skip non-node elements like font, hook, etc.)
        for child in root:
            if child.tag == 'node':
                self._print_tree_as_titles(child, level + 1)

        if level == 1:
            pass
        elif level == 2:
            print("\\end{itemize}")
            print("\\end{frame}")
        elif level == 3:
            pass
        elif level == 4:
            pass
