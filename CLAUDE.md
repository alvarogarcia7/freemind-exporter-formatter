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

### Value Objects (orgmode_dates.py)
Frozen dataclasses representing immutable data:
- `DateValue`, `DateTimeValue`: Date/time representations
- `TimeEntry`, `Section`, `DateEntry`: Date reading structures
- `TaskEntry`, `TaskInfo`, `ProjectInfo`: Task and project hierarchies
- `DateReader`, `DateTimeReader`: Factory methods for XML parsing

### Helper Classes (orgmode_helpers.py)
Static utility methods organized by responsibility:
- `NodeTreeHelper`: Tree traversal and node classification
- `DateTimeHelper`: Datetime operations
- `DurationFormatter`: Time duration calculations and formatting
- `HierarchicalNodeProcessor`: Three-phase node processing

### Formatters
- `orgmode.py`: Main ORGMode output formatter
- `orgmode_date_sections.py`: Date section formatting
- `orgmode_lists.py`: List formatting

All three formatters inherit from `NodeTreeHelper` mixin and use static methods from utility classes.
