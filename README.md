## Freemind Mindmap Formatter

Export [Freemind][0] mindmaps.

[0]: http://freemind.sourceforge.net/wiki/index.php/Main_Page

## Scope
### Out of scope

  * HTML nodes

### Features

  * Specify a formatter from the command-line
  * Formatters are specified as Python programs

## How to use it

### Setup

This project uses [uv](https://docs.astral.sh/uv/) for Python package and virtual environment management.

To set up the project:

```bash
# Install uv (if not already installed)
# See https://docs.astral.sh/uv/getting-started/installation/

# uv will automatically create a virtual environment and install dependencies
uv sync
```

### Running tests

```bash
make test              # Run all tests (typecheck + e2e)
make typecheck         # Run mypy type checker in strict mode
make test-e2e          # Run end-to-end tests
```

### Sample usage

See examples in [approval_tests](tests%2Fapproval_tests):

```bash
python3 main.py --input ./data/test1.mm --formatter leaf_as_text.py
```

### Extending the formatters

This project has been designed so that the formatting is separated from the XML representation.

To use another Exporter, implement another child of `MindmapExporter`, then call it in the main arguments.
See example invocation in the [approval_tests](tests%2Fapproval_tests) folder.

There is a sample exporter in the `print_as_titles.py` file.
