# HEDGE - Hierarchical Evolutionary Darwin-Green Engine

A state-of-the-art code optimization system using evolutionary strategies to improve Python code efficiency.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# OR use virtualenv (recommended)
source .venv/bin/activate  # If you have .venv already
pip install -r requirements.txt

# Basic optimization
python3 hedge.py optimize examples/fibonacci.py examples/fibonacci_test.py

# With visualizations
python3 hedge.py optimize examples/fibonacci.py examples/fibonacci_test.py --visualize

# Advanced: LLM-based semantic optimization
export GEMINI_API_KEY="your-api-key"
python3 hedge.py optimize mycode.py mycode_test.py --enable-semantic --visualize
```

## 📋 Features

- **IR-Only Architecture**: All mutations operate on a strict Intermediate Representation
- **Multiple Mutation Strategies**: Structural, semantic (LLM-based), and advanced optimizations
- **Context-Aware Mutations**: Dependency analysis ensures semantics-preserving transformations
- **Pareto Optimization**: Multi-objective optimization for energy and execution time
- **Comprehensive Visualizations**: Charts, graphs, and interactive HTML reports
- **Rich CLI**: Beautiful console output with progress tracking

## 🛠️ Installation

```bash
# Clone repository
git clone <repository-url>
cd HEDGE

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install for better UI
pip install rich matplotlib
```

## 📖 Usage

### Commands

**Optimize Code**
```bash
python3 hedge.py optimize <target.py> <tests.py> [options]

Options:
  --generations N          Number of evolutionary generations (default: 5)
  --enable-semantic        Enable LLM-based semantic mutations
  --enable-advanced        Enable advanced optimizations (constant folding, DCE)
  --visualize             Generate visualizations after optimization
  --save-ir               Save IR snapshots for debugging
  --verbose               Detailed logging
```

**Analyze Code**
```bash
python3 hedge.py analyze <code.py>
```

**Generate Visualizations**
```bash
python3 hedge.py visualize <results_dir>
```

### Examples

```bash
# Simple optimization
python3 hedge.py optimize fibonacci.py fibonacci_test.py --generations 10

# Full-featured optimization with LLM
export GEMINI_API_KEY="..."
python3 hedge.py optimize mycode.py tests.py \
  --generations 20 \
  --enable-semantic \
  --enable-advanced \
  --visualize \
  --verbose

# Analyze code complexity
python3 hedge.py analyze complex_algorithm.py
```

## 📊 Output

Optimization results are saved to `experiments/run_TIMESTAMP/`:
- `config.json` - Experiment configuration
- `pareto_results.json` - All Pareto-optimal solutions
- `statistics.json` - Mutation statistics
- `visualizations/` - Charts and HTML report
- `<target>_optimized.py` - Best solution (lowest energy)

## 🏗️ Architecture

```
HEDGE/
├── hedge.py                 # Main CLI entry point
├── src/
│   ├── domain/             # Core business logic
│   │   ├── ir/            # IR schema, validators, metrics
│   │   └── interfaces.py  # Abstract base classes
│   ├── application/        # Use cases
│   │   ├── mutators/      # Mutation strategies
│   │   └── engine/        # Evolutionary engine
│   └── infrastructure/     # External integrations
│       ├── parsing/       # Python → IR
│       ├── codegen/       # IR → Python
│       ├── llm/          # LLM clients
│       └── execution/    # Code runner
├── tests/                  # Test suite
└── examples/              # Example code
```

## 🧪 Testing

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ --cov=src --cov-report=html

# Run specific test
python3 -m pytest tests/test_parser.py -v
```

## 📚 Documentation

- **CLI.md** - Complete CLI documentation
- **TESTING.md** - Testing guide
- **src/** - Inline code documentation

## 🔬 Key Concepts

### IR-Only Mutations
All code transformations operate on a strict Intermediate Representation (IR), ensuring type safety and preventing string-based code manipulation errors.

### Multi-Objective Optimization
HEDGE optimizes for both energy consumption and execution time, maintaining a Pareto front of non-dominated solutions.

### Context-Aware Transformations
Mutation context tracks symbol tables and data dependencies, ensuring transformations preserve program semantics.
