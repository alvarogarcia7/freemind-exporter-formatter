import sys
import xml.etree.ElementTree as xml
from typing import Any


class MindmapExporter:
    def __init__(self) -> None:
        self.out = sys.stdout
        self.lines: list[str] = []
        """
        The parsed result of the XML tree
        :type: Any - depends on the exporter
        """
        self.result: Any = None

    def export(self, tree: xml.Element) -> None:
        self.parse(tree)
        self.lines = self.format()
        self.print()

    def parse(self, tree: xml.Element) -> None:
        """
        Parse the XML tree and store the result in `self.result`
        :param tree:
        """
        raise NotImplementedError()

    def print(self) -> None:
        """
        Print the formatted output lines to the output stream
        The output content is printed line by line from the list `self.lines`
        """
        for line in self.lines:
            print(line, file=self.out)

    def format(self) -> list[str]:
        """
        Format the parsed result into a list of output lines
        :return: list of formatted output lines
        """
        return self.lines.copy()
