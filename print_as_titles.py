from mindmap_exporter import MindmapExporter


class Formatter(MindmapExporter):
    def export(self, tree):
        self._print_tree(tree)

    def _print_tree(self, root):
        self._print_tree_as_titles(root, 1)

    def _print_tree_as_titles(self, root, level):
        print(("#" * level) + " " + root.attrib['TEXT'])
        for child in root:
            self._print_tree_as_titles(child, level + 1)
