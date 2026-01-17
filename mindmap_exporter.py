import sys
import xml.etree.ElementTree as xml


class MindmapExporter:
    def __init__(self) -> None:
        self.out = sys.stdout
        self.lines: list[str] = []

    def export(self, tree: xml.Element) -> None:
        self.parse(tree)
        self.print()

    def parse(self, tree: xml.Element) -> None:
        raise NotImplementedError()

    def print(self) -> None:
        for line in self.lines:
            print(line, file=self.out)
