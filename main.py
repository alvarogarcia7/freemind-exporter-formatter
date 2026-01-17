import argparse
import sys
import xml.etree.ElementTree as xml
from typing import Optional, TextIO


class MindMapFormatter:
    def __init__(self, statement_path: str, formatter_name: str, output_file: Optional[TextIO] = None) -> None:
        self.path = statement_path
        self.program = formatter_name
        self.output_file = output_file

    def read(self) -> None:
        with open(self.path, "r") as file:
            tree = xml.parse(file)
            """
            Skip the topmost node, a container for the head of the mindmap
            :param tree: the whole mindmap
            :return: the head of the mindmap, with its children
            """
            map_root = tree.getroot()
            # Handle both Freemind and FreePlane formats
            # Freemind: <map><node>...</node></map>
            # FreePlane: <map><bookmarks>...</bookmarks><node>...</node></map>
            root = self._get_root_node(map_root)
            self._print_tree(root)

    def _get_root_node(self, map_root: xml.Element) -> xml.Element:
        """
        Extract the root node from the map, handling both Freemind and FreePlane formats.

        :param map_root: the map element
        :return: the root node element
        """
        for child in map_root:
            if child.tag == 'node':
                return child
        raise ValueError("No node element found in map")

    def _print_tree(self, root: xml.Element) -> None:
        module = __import__(self.program)
        formatter = module.Formatter(output=self.output_file)
        formatter.export(root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Configuration
    parser.add_argument("--input", required=True)
    parser.add_argument("--formatter", required=True, default="print_as_titles")
    parser.add_argument("--output", default=None, help="Output file (default: stdout)")

    args = parser.parse_args()
    args.formatter = args.formatter.removesuffix(".py")

    # Open output file if specified, otherwise use stdout
    output_file: Optional[TextIO] = None
    if args.output:
        output_file = open(args.output, "w")

    try:
        MindMapFormatter(args.input, args.formatter, output_file).read()
    finally:
        if output_file:
            output_file.close()
