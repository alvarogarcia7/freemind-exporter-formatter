from mindmap_exporter import MindmapExporter
import xml.etree.ElementTree as xml


class Formatter(MindmapExporter):
    def parse(self, tree: xml.Element) -> None:
        self._open_block_itemize = False
        self._open_block_subitemize = False
        self.lines = self._format_tree_as_titles(tree, 0)

    def format(self) -> list[str]:
        return self.lines.copy()

    def _format_tree_as_titles(self, root: xml.Element, level: int) -> list[str]:
        lines: list[str] = []

        any_children_has_richcontent = any(child.tag == "richcontent" for child in root)
        assert not any_children_has_richcontent, (
            f"Node attributes cannot be contain .tag=richcontent. Node: {root}, {root.attrib}"
        )

        if root.tag == "richcontent":
            assert False, (
                f"Richcontent should not be present at level {level}. Node: {root}, {root.attrib}"
            )

        if "TEXT" not in root.attrib:
            for child in root:
                lines.extend(self._format_tree_as_titles(child, level))
            return lines

        has_children = len(root) > 0
        node_text = root.attrib["TEXT"]
        levels_allowed_to_be_empty = [2]
        if level not in levels_allowed_to_be_empty:
            assert node_text, (
                f"Node text cannot be empty at level {level}. Node: {root}, {root.attrib}"
            )
        # print(f"DEBUG: {level}, tag={root.tag} {{{node_text}}}")

        if is_preformatted := node_text.startswith("% PRE"):
            lines += node_text.splitlines(keepends=False)
        else:
            # print(f"DEBUG: {level}, {{{node_text}}}")
            if level == 1:
                lines.append(f"""
\\section{{{node_text}}}
""")
            elif level == 2:
                if node_text:
                    lines.append(f"""
\\subsection{{{node_text}}}
""")
            elif level == 3:
                lines.append(f"""
\\begin{{frame}} % Open Frame '{node_text}'
\t\\frametitle{{{node_text}}}""")

                if has_children:
                    lines.append("""
\t\\begin{itemize}""")
                    self._open_block_itemize = True

            elif level == 4:
                comment = (
                    f" % Item with {len(root)} subitems"
                    if has_children
                    else " % Item without subitems"
                )
                lines.append(((level - 2) * "\t") + f"\\item {node_text}{comment}")
                if has_children:
                    lines.append(
                        ((level - 2) * "\t")
                        + f"\\begin{{itemize}} % Subitem in Item '{node_text}'"
                    )
                    self._open_block_subitemize = True

            elif level == 5:
                assert self._open_block_subitemize
                lines.append(((level - 2) * "\t") + f"\\item {node_text} % Subitem")

        # Whether is_preformatted is True or False, we always want to process the children
        for child in root:
            if child.tag == "node":
                lines.extend(self._format_tree_as_titles(child, level + 1))
        # Whether is_preformatted is True or False, we always want to process the children

        if not is_preformatted:
            if level == 4:
                if self._open_block_subitemize:
                    lines.append(
                        ((level - 2) * "\t")
                        + f"\\end{{itemize}} % Close Subitem in Item '{node_text}'"
                    )
                    self._open_block_subitemize = False
            elif level == 3:
                if self._open_block_itemize:
                    lines.append(((level - 2) * "\t") + "\\end{itemize}")
                    self._open_block_itemize = False

                lines.append(
                    ((level - 2 - 1) * "\t")
                    + f"\\end{{frame}} % Close Frame '{node_text}'\n"
                )
            elif level == 2:
                pass
            elif level == 1:
                pass

        return lines
