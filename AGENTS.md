1→# Agent Guide
2→
3→## Commands
4→- **Setup**: `uv sync` (creates `.venv/` and installs deps)
5→- **Build**: N/A (interpreted Python)
6→- **Lint**: `make typecheck` (mypy strict mode)
7→- **Test**: `make test` (mypy + pytest)
8→- **Dev**: `python3 main.py --input <file.mm> --formatter <formatter.py>`
9→
10→## Tech Stack
11→- Python 3.9+ with `uv` package manager
12→- XML parsing via `xml.etree.ElementTree`
13→- Testing: pytest + ApprovalTests
14→- Type checking: mypy (strict mode)
15→
16→## Architecture
17→- `main.py`: CLI entry point, loads formatter modules dynamically
18→- `mindmap_exporter.py`: Base class for exporters
19→- `*_exporter.py` / `*.py`: Formatter implementations (inherit `MindmapExporter`)
20→- `data/`: Input mindmap files (.mm)
21→- `tests/`: Pytest tests with approval files
22→
23→## Code Conventions
24→- Type hints required (mypy strict mode enforced)
25→- Formatters implement `Formatter` class with `export(tree: xml.Element)` method
26→- Private methods prefixed with `_`
27→
