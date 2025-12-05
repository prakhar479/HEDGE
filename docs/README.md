# HEDGE Documentation Portal

Welcome to the documentation for HEDGE (Hierarchical Evolutionary Darwin-Green Engine).

## 📚 Guides

-   **[Setup Guide](SETUP.md)**: Installation, environment configuration, and running your first experiment.
-   **[CLI Reference](CLI.md)**: Detailed documentation for the `hedge.py` command-line interface.
-   **[Contributing](CONTRIBUTING.md)**: Guidelines for contributing code and docs to HEDGE.

## 🏗️ Technical Documentation

-   **[Architecture](ARCHITECTURE.md)**: High-level system design, IR structure, and pipeline data flow.
-   **[Mutators](MUTATORS.md)**: Deep dive into the mutation strategies (Structural, Semantic, Advanced).
-   **[Directory Structure](../README.md#architecture)**: Overview of the codebase layout.

## 🧪 Development

-   **Testing**: Run tests using `pytest`.
    ```bash
    python -m pytest tests/ -v
    ```

## 🔍 Key Concepts

-   **IR-Only**: All optimizations occur on the Intermediate Representation.
-   **Pareto Optimization**: Balancing Energy vs Time.
-   **Validation**: Every mutation is validated before execution.
