# Development Guidelines for Claude

## Pre-Commit Hooks

Before committing any changes, you **MUST** run the pre-commit hooks:

```bash
make pre-commit
```

This runs the following checks on all staged files:
- Trailing whitespace trimming
- EOF file fixing
- YAML validation
- Large file detection
- Merge conflict detection
- JSON validation
- Private key detection
- Ruff (linting and formatting)
- Flake8 (linting)
- mypy (type checking with strict mode)
- Unit tests

**All checks must pass before committing.** If any check fails, the command will exit with an error and describe what needs to be fixed.

## Pre-Push Hooks

Before pushing to the remote repository, ensure:
1. All pre-commit checks pass (run `make pre-commit`)
2. All tests pass (run `make test`)
3. The code builds without errors (run `make build` if applicable)

## Commit Workflow

1. Make code changes
2. Stage files: `git add <files>` or `git add -A`
3. Run pre-commit hooks: `make pre-commit`
4. Fix any issues reported by hooks
5. Once all checks pass, create commit with descriptive message
6. Push to remote (if authorized)

## Type Checking

The project uses mypy with strict mode enabled:

```bash
mypy . --exclude .venv --strict --warn-unreachable --warn-return-any --disallow-untyped-calls
```

All type annotations must be explicit and complete. Key requirements:
- Generic types must include type parameters (e.g., `Dict[str, Any]` not `dict`)
- Optional values must use `Optional[T]`
- Function return types must be specified
- No untyped function calls are allowed (use `# type: ignore` only as a last resort)

## Testing

Run all tests with:

```bash
make test
```

This runs:
1. mypy type checking
2. pytest with all test files

All 203 tests must pass.

## Code Organization

### mindmap Package
Core mindmap reading and tree traversal:
- `mindmap/reader.py`:
  - `NodeTreeHelper`: Tree traversal and node classification (is_leaf, get_node_children, extract_tags_from_node)
  - `DateReader`: XML date node reading and parsing
  - `DateTimeReader`: XML datetime node reading and parsing
- `mindmap/models.py`: Value objects representing immutable mindmap data
  - `DateValue`: Date representation with formatting
  - `DateTimeValue`: Datetime representation with formatting
  - `TimeEntry`: Time entry with start/end times
  - `Section`: Named section (WORKLOG, TIMES, TODO, etc.)
  - `DateEntry`: Date with associated sections

### worklog Package
Worklog-specific formatting and TODO logic:
- `worklog/format.py`:
  - `TodoHelper`: TODO detection and text processing (is_todo, clean_todo_text)
- `worklog/helpers.py`:
  - `DateTimeHelper`: Datetime operations (find_end_time, extract_comments)
  - `DurationFormatter`: Time duration calculations and formatting
  - `HierarchicalNodeProcessor`: Three-phase node processing
- `worklog/models.py`: Value objects for worklog task and project data
  - `TaskEntry`: Worklog entry with task name and time range
  - `TaskInfo`: Task with multiple entries
  - `ProjectInfo`: Project containing multiple tasks

### Formatters (root level)
- `orgmode.py`: Main ORGMode worklog output formatter
- `orgmode_date_sections.py`: Date section formatting
- `orgmode_lists.py`: List formatting

All three formatters inherit from `NodeTreeHelper` mixin and use static methods from utility classes.
