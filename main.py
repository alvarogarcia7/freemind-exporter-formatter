import argparse
import xml.etree.ElementTree as xml


class MindMapFormatter:
    def __init__(self, statement_path: str, formatter_name: str):
        self.path = statement_path
        self.program = formatter_name

    def read(self):
        with open(self.path, "r") as file:
            tree = xml.parse(file)
            root = tree.getroot()[0]
            self._print_tree(root)

    def _print_tree(self, root):
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
