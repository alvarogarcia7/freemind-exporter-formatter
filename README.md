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

### Sample usage

See examples in `[approval_tests](tests%2Fapproval_tests)`

### Extending the formatters

This project has been designed so that the formatting is separated from the XML representation.

To use another Exporter, implement another child of `MindmapExporter`, then call it in the main arguments.
See example invocation in the `test-e2e` make goal.

There is a sample exporter in the `print_as_titles.py` file.
