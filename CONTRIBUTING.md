# Contributing to Issue Tracker API

Thank you for considering contributing to this project! This document outlines the process and guidelines.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/issue-tracker-api.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest`
6. Commit your changes: `git commit -m 'Add some feature'`
7. Push to the branch: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

See README.md for detailed setup instructions.

## Code Style

- Follow PEP 8 guidelines
- Use Black for formatting: `black src/`
- Use Ruff for linting: `ruff check src/`
- Add type hints where appropriate
- Write docstrings for public functions

## Testing

- Write tests for new features
- Ensure all tests pass: `pytest`
- Maintain >= 70% code coverage
- Use pytest fixtures for test data
- Separate unit and integration tests

## Pull Request Guidelines

- Keep PRs focused (one feature/fix per PR)
- Update documentation if needed
- Add tests for new functionality
- Ensure CI/CD pipeline passes
- Write clear commit messages
- Reference related issues

## Commit Message Format

```
type(scope): brief description

Detailed description if needed

Fixes #issue_number
```

Types: feat, fix, docs, style, refactor, test, chore

## Questions?

Open an issue for discussion before starting major changes.
