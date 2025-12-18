# Contributing to HEDGE

We welcome contributions to HEDGE! This document provides guidelines for contributing to the layered code optimization system.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/prakhar479/HEDGE.git
   cd HEDGE
   ```

2. **Set up environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   
   # Optional: Enhanced development tools
   pip install rich matplotlib pytest-cov
   ```

3. **Run tests**:
   ```bash
   # All tests
   python -m pytest tests/ -v
   
   # Layer-specific tests
   python -m pytest tests/test_layered_system.py -v
   python -m pytest tests/test_enhanced_mutators.py -v
   
   # With coverage
   python -m pytest tests/ --cov=src --cov-report=html
   ```

## Development Standards

### Code Style
- Follow PEP 8 guidelines
- Use descriptive variable and function names
- Add typing hints to all function signatures
- Use dataclasses for structured data
- Follow the layered architecture patterns

### Layered Architecture Principles
- **Layer Separation**: Each mutation layer should be independent
- **IR-Only Philosophy**: No direct string/AST manipulation
- **Orchestrated Execution**: Use `MutationOrchestrator` for coordination
- **Metadata Tracking**: Include confidence scores and descriptions

### IR-Only Philosophy
- Do not parse/modify strings directly for AST manipulation
- Use the IR schema (`src/domain/ir/schema.py`)
- If you add a new node type, update `validators.py` and `python_codegen.py`
- All mutations must preserve semantic equivalence

### Pull Requests
1. Create a feature branch (`git checkout -b feature/my-feature`)
2. Follow the layered architecture patterns
3. Add comprehensive tests for new layers/mutators
4. Ensure all tests pass
5. Update documentation if adding new features
6. Submit a Pull Request with clear description

## Adding New Mutators

### Layer-Based Mutator Development

See [MUTATORS.md](MUTATORS.md) for detailed information on the layered mutation system.

**Basic Structure**:
```python
from src.application.mutators.base import LayeredMutator, MutationLayer, MutationResult

class MyNewMutator(LayeredMutator):
    def __init__(self):
        super().__init__(MutationLayer.SYNTACTIC)  # Choose appropriate layer
    
    def get_available_strategies(self) -> List[str]:
        return ["strategy1", "strategy2"]
    
    def _apply_mutations(self, ir: Module) -> List[MutationResult]:
        # Implementation here
        pass
```

**Testing New Mutators**:
```bash
# Test your mutator
python -m pytest tests/test_your_mutator.py -v

# Integration test
python hedge.py optimize examples/target.py examples/test_target.py --layers your_layer
```

### Layer Guidelines

**Semantic Layer** (🧠):
- High-level algorithmic improvements
- Requires LLM integration
- Focus on Big-O complexity reduction
- Algorithm selection and intent optimization

**Algorithmic Layer** (📊):
- Data structure optimizations
- Complexity improvements
- No LLM required
- Mathematical and structural optimizations

**Syntactic Layer** (🐍):
- Python idiom improvements
- Code pattern optimization
- Optional LLM enhancement
- Language-specific optimizations

**Micro Layer** (⚡):
- Low-level optimizations
- Constant folding, dead code elimination
- No external dependencies
- Fast, safe transformations

## Testing Guidelines

### Test Structure
```bash
tests/
├── test_layered_system.py      # Layer orchestration tests
├── test_enhanced_mutators.py   # Individual mutator tests
├── test_crossover.py          # Genetic operations tests
└── test_e2e_new_system.py     # End-to-end integration tests
```

### Writing Tests
- Test each mutation strategy individually
- Include edge cases and error conditions
- Verify semantic preservation
- Test layer coordination
- Include performance benchmarks

### Running Specific Tests
```bash
# Layer system tests
python -m pytest tests/test_layered_system.py::test_layer_orchestration -v

# Mutator tests
python -m pytest tests/test_enhanced_mutators.py::TestConstantOptimizer -v

# Integration tests
python -m pytest tests/test_e2e_new_system.py -v
```

## Documentation

When contributing:
- Update relevant documentation in `docs/`
- Add docstrings to new classes and methods
- Include examples in docstrings
- Update CLI help text if adding new options
- Add entries to `MUTATORS.md` for new mutation strategies

## Code Review Process

1. **Automated Checks**: Ensure tests pass and code follows style guidelines
2. **Architecture Review**: Verify adherence to layered architecture
3. **Performance Review**: Check for performance implications
4. **Documentation Review**: Ensure documentation is updated
5. **Integration Testing**: Test with existing system components
