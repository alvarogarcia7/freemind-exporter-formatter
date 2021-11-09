import argparse
import xml.etree.ElementTree as xml
from typing import Dict


class MindMapFormatter:
    def __init__(self, statement_path: str, formatter_name: str):
        self.path = statement_path
        self.program = formatter_name

    def read(self) -> None:
        with open(self.path, "r") as file:
            tree = xml.parse(file)
            root = self._get_center_node(tree)
            self._print_tree(root)

    @staticmethod
    def _get_center_node(tree: xml.ElementTree) -> xml.Element:
        """
        Skip the topmost node, a container for the head of the mindmap
        :param tree: the whole mindmap
        :return: the head of the mindmap, with its children
        """
        return tree.getroot()[0]

    def _print_tree(self, root: xml.Element) -> None:
        module = __import__(self.program)
        module.Formatter().export(root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Configuration
    parser.add_argument("--input", required=True)
    parser.add_argument("--formatter", required=True, default="print_as_titles")

    args = parser.parse_args()
    args.formatter = args.formatter.removesuffix(".py")

    MindMapFormatter(args.input, args.formatter).read()
