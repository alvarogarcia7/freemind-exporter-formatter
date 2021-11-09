import argparse
import xml.etree.ElementTree as xml


class MindMapFormatter:
    def __init__(self, statement_path: str):
        self.path = statement_path

    def read(self):
        with open(self.path, "r") as file:
            tree = xml.parse(file)
            root = tree.getroot()[0]
            self._print_tree(root)

    def _print_tree(self, root):
        # program = "print_as_titles"
        # module = __import__(program)
        from print_as_titles import TitlesMindMapFormatter
        TitlesMindMapFormatter().export(root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Configuration
    parser.add_argument("--input")

    MindMapFormatter(parser.parse_args().input).read()
