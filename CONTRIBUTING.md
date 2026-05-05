# Contributing to SimForge3D

Thank you for your interest in contributing to SimForge3D! This document provides guidelines and information for contributors.

## Development Setup

```bash
git clone https://github.com/yablokolabs/SimForge3D.git
cd SimForge3D
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

All tests run headless and do not require a display server or GPU.

## Code Quality

We use the following tools, all configured in `pyproject.toml`:

- **ruff** — linting and formatting
- **mypy** — static type checking
- **pytest** — testing

Run all checks before submitting a PR:

```bash
ruff check simforge3d tests examples
ruff format --check simforge3d tests examples
mypy simforge3d
pytest
```

## Pull Request Process

1. Fork the repository and create a feature branch from `main`.
2. Write tests for new functionality.
3. Ensure all checks pass locally.
4. Submit a pull request with a clear description of the change.
5. PRs require passing CI and at least one review before merging.

## Commit Messages

Use clear, descriptive commit messages. Prefer the imperative mood:

- ✅ `Add navigation scenario timeout handling`
- ✅ `Fix collision detection at world bounds`
- ❌ `Fixed stuff`
- ❌ `Updates`

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for an overview of the system design.

## Adding a Scenario

1. Create a new file in `simforge3d/scenarios/`.
2. Subclass `BaseScenario` and implement `setup`, `success`, and `reward`.
3. Register it in `simforge3d/scenarios/registry.py`.
4. Add tests in `tests/`.

## Code Style

- Follow existing patterns in the codebase.
- Use type annotations for all public APIs.
- Keep modules focused and imports minimal.
- Headless-first: simulation logic must work without Panda3D imported.

## Reporting Bugs

Open an issue with:

- Python version and OS
- Steps to reproduce
- Expected vs actual behavior
- Full traceback if applicable

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
