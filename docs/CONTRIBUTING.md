# Contributing to HEDGE

We welcome contributions to HEDGE! This document provides guidelines for contributing to the project.

## Development Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/prakhar479/HEDGE.git
    cd HEDGE
    ```

2.  **Set up environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Run tests**:
    ```bash
    python -m pytest tests/
    ```

## Development Standards

### Code Style
-   Follow PEP 8 guidelines.
-   Use descriptive variable and function names.
-   Add typing hints (`typing`) to all function signatures.

### IR-Only Philosophy
-   Do not parse/modify strings directly for AST manipulation.
-   Use the IR schema (`src/domain/ir/schema.py`).
-   If you add a new node type, update `validators.py` and `python_codegen.py`.

### Pull Requests
1.  Create a feature branch (`git checkout -b feature/my-feature`).
2.  Commit your changes with clear messages.
3.  Ensure all tests pass.
4.  Submit a Pull Request.

## Adding Mutators

See [MUTATORS.md](MUTATORS.md) for details on implementing new mutation strategies.
