# HEDGE Documentation Portal

Welcome to the documentation for HEDGE (Hierarchical Evolutionary Darwin-Green Engine) - a layered code optimization system.

## � Quick Start

- **[Setup Guide](SETUP.md)** - Installation, environment setup, and first optimization
- **[CLI Reference](CLI.md)** - Complete command-line interface documentation

## 📚 User Guides

- **[Setup Guide](SETUP.md)** - Installation, LLM configuration, and running examples
- **[CLI Reference](CLI.md)** - Detailed command-line interface with layered system options
- **[Contributing](CONTRIBUTING.md)** - Guidelines for contributing to HEDGE

## 🏗️ Technical Documentation

- **[Architecture](ARCHITECTURE.md)** - Layered system design, IR structure, and data flow
- **[Mutators](MUTATORS.md)** - Hierarchical mutation layers and optimization strategies
- **[Directory Structure](../README.md#layered-architecture)** - Codebase organization

## 🧪 Development

**Testing**:
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Test specific layer
python -m pytest tests/test_layered_system.py -v
```

**Layer Development**:
```bash
# List available mutators by layer
python hedge.py list-mutators

# Test new mutator
python -m pytest tests/test_enhanced_mutators.py -v
```

## 🔍 Key Concepts

- **Hierarchical Layers**: 4-layer mutation system (Semantic → Algorithmic → Syntactic → Micro)
- **IR-Only Transformations**: All optimizations operate on Intermediate Representation
- **Pareto Optimization**: Multi-objective optimization balancing energy vs execution time
- **Context-Aware Mutations**: Dependency analysis ensures semantic preservation
- **Orchestrated Execution**: Intelligent layer coordination and mutation ordering

## 📊 Layer Overview

| Layer | Purpose | Examples | LLM Required |
|-------|---------|----------|--------------|
| 🧠 **Semantic** | Algorithm intent | O(n²) → O(n log n) | Yes |
| 📊 **Algorithmic** | Data structures | List → Set for membership | No |
| 🐍 **Syntactic** | Python idioms | Loops → comprehensions | Optional |
| ⚡ **Micro** | Low-level opts | Constant folding | No |
