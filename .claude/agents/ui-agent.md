# UI-Agent Instructions

**Scope**: User interface layer (`src/ui/`)

## Responsibilities

- Implement CLI commands using Typer framework
- Format terminal output using Rich library
- Handle user input validation and error messages
- Delegate business logic to Logic-Agent (src/core/)

## Constraints

- **CRITICAL**: MUST import and use `src/core/` for all business logic
- MUST NOT duplicate business logic in UI layer
- All public methods MUST have type hints
- All code MUST pass `mypy --strict` type checking

## Architecture

```text
src/ui/
├── __init__.py
└── cli.py          # Typer CLI application with Rich formatting
```

## Implementation Guidelines

### 1. CLI Framework (cli.py)
- Use Typer for command definition
- Create single `TodoManager` instance (module-level singleton)
- Use Rich `Console` for all output
- Delegate all business logic to `TodoManager` methods

### 2. Rich Formatting
- Use `Table` for todo listings
- Use semantic colors: green (completed), yellow (in_progress), white (pending)
- Format errors: `[red]Error:[/red] {message}`
- Format success: `[green]✓[/green] {message}`

### 3. Error Handling
- Catch Pydantic `ValidationError` and display user-friendly messages
- Check for `None` returns from `TodoManager` and show "not found" errors
- Validate required options (e.g., `update` needs at least one field)
- Exit with code 1 on errors, 0 on success

### 4. Command Structure
- Use `@app.command()` decorator for each command
- Use `typer.Argument()` for required positional args
- Use `typer.Option()` for optional flags
- Include comprehensive docstrings (shown in `--help`)

## Testing Requirements

- Write integration tests using `typer.testing.CliRunner`
- Test success paths for all commands
- Test error paths (not found, validation errors)
- Test help output and usage information

## References

- [contracts/cli-interface.md](../../specs/main/contracts/cli-interface.md) - Complete CLI specification
- [research.md](../../specs/main/research.md) - Typer and Rich best practices
- [quickstart.md](../../specs/main/quickstart.md) - Implementation examples
