# HEDGE Documentation

## Core Documentation

### User Guides
- [CLI Usage](CLI.md) - Complete command-line interface documentation
- [Testing Guide](TESTING.md) - How to run and write tests
- [Setup Guide](SETUP.md) - Installation and configuration

### Architecture
- Main entry point: `hedge.py`
- IR schema: `src/domain/ir/schema.py`
- Mutators: `src/application/mutators/`
- Engine: `src/application/engine/evolution.py`

## Quick Reference

### Common Commands
```bash
# Optimize
python3 hedge.py optimize <target> <tests> [--visualize]

# Analyze
python3 hedge.py analyze <code>

# Visualize
python3 hedge.py visualize <results_dir>
```

### Architecture Principles
1. **IR-Only**: All mutations operate on Intermediate Representation
2. **Clean Architecture**: Domain → Application → Infrastructure
3. **Type Safety**: Pydantic models for IR nodes
4. **Validation Gates**: All variants validated before execution

See individual module docstrings for implementation details.
