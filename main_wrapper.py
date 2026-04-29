#!/usr/bin/env python3
"""Wrapper script for main.py to make it executable and genzshcomp-compatible."""

from main import MindMapFormatter
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="main")
    # Configuration
    parser.add_argument("--input", required=True)
    parser.add_argument("--formatter", required=True, default="print_as_titles")
    parser.add_argument("--output", default=None, help="Output file (default: stdout)")

    args = parser.parse_args()
    args.formatter = args.formatter.removesuffix(".py")

    # Open output file if specified, otherwise use stdout
    output_file = None
    if args.output:
        output_file = open(args.output, "w")

    try:
        MindMapFormatter(args.input, args.formatter, output_file).read()
    finally:
        if output_file:
            output_file.close()
