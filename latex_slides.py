from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml


class Formatter(MindmapExporter):
    def export(self, tree: xml.Element) -> None:
        self._print_tree(tree)

    def _print_tree(self, root: xml.Element) -> None:
        self._print_tree_as_titles(root, 0)

    def _print_tree_as_titles(self, root: xml.Element, level: int) -> None:
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

        for child in root:
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
