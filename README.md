# HEDGE - Hierarchical Evolutionary Darwin-Green Engine

A state-of-the-art **layered code optimization system** using evolutionary strategies to improve Python code efficiency through hierarchical mutation layers.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# OR use virtualenv (recommended)
source .venv/bin/activate  # If you have .venv already
pip install -r requirements.txt

# Micro-optimizations only (constant folding, dead code elimination)
python3 hedge.py optimize examples/target.py examples/test_target.py --level micro

# Standard layered optimization (micro + syntactic + algorithmic)
python3 hedge.py optimize examples/target.py examples/test_target.py --level standard

# Advanced with semantic layer (requires LLM API key)
export GEMINI_API_KEY="your-api-key"
python3 hedge.py optimize examples/target.py examples/test_target.py --level advanced

# Custom layer selection
python3 hedge.py optimize examples/target.py examples/test_target.py --layers micro,algorithmic
```

## 📋 Features

- **Hierarchical Layered Architecture**: 4-layer mutation system (Semantic → Algorithmic → Syntactic → Micro)
- **IR-Only Mutations**: All transformations operate on a strict Intermediate Representation
- **34+ Optimization Strategies**: Comprehensive mutation strategies across all abstraction levels
- **Context-Aware Transformations**: Dependency analysis ensures semantics-preserving mutations
- **Multi-Objective Optimization**: Pareto front optimization for energy vs execution time
- **LLM-Enhanced Semantic Layer**: AI-powered algorithm and intent optimization
- **Granular Control**: Fine-grained control over optimization layers and strategies
- **Comprehensive Visualizations**: Charts, graphs, and interactive HTML reports
- **Rich CLI**: Beautiful console output with progress tracking and layer statistics

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

Optimization Levels:
  --level micro           Micro-optimizations only (constant folding, dead code elimination)
  --level basic           Micro + syntactic optimizations (Python idioms, patterns)
  --level standard        Basic + algorithmic optimizations (data structures, complexity)
  --level advanced        Standard + semantic optimizations (algorithm intent, LLM-based)
  --level aggressive      All layers enabled

Layer Control:
  --layers LAYERS         Comma-separated list of specific layers: semantic,algorithmic,syntactic,micro
  --legacy-mode          Use original mutator system instead of layered approach

Other Options:
  --generations N         Number of evolutionary generations (default: 5)
  --llm-provider PROVIDER LLM provider for semantic layer (gemini, openai)
  --exclude-mutators LIST Exclude specific mutator classes
  --visualize            Generate visualizations after optimization
  --save-ir              Save IR snapshots for debugging
  --verbose              Detailed logging
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
# Micro-optimizations only (fast, safe)
python3 hedge.py optimize bubble_sort.py test_sort.py --level micro --generations 5

# Standard layered optimization (recommended)
python3 hedge.py optimize algorithm.py test_algo.py --level standard --generations 10

# Advanced semantic optimization with LLM
export GEMINI_API_KEY="your-api-key"
python3 hedge.py optimize complex_code.py tests.py --level advanced --generations 15 --visualize

# Custom layer selection
python3 hedge.py optimize code.py tests.py --layers algorithmic,micro --generations 8

# Legacy mode (original system)
python3 hedge.py optimize code.py tests.py --legacy-mode --level advanced

# List available mutators and layers
python3 hedge.py list-mutators

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

## 🏗️ Layered Architecture

```
HEDGE/
├── hedge.py                 # Main CLI entry point with layered controls
├── src/
│   ├── domain/             # Core business logic
│   │   ├── ir/            # IR schema, validators, metrics
│   │   └── interfaces.py  # Abstract base classes
│   ├── application/        # Layered mutation system
│   │   ├── mutators/      # Hierarchical mutation layers
│   │   │   ├── base.py           # Layered abstraction framework
│   │   │   ├── semantic_layer.py    # Algorithm intent optimization
│   │   │   ├── algorithmic_layer.py # Data structure & complexity
│   │   │   ├── syntactic_layer.py   # Python idioms & patterns
│   │   │   └── micro_layer.py       # Low-level optimizations
│   │   └── engine/        # Enhanced evolutionary engine
│   │       ├── evolution.py        # Layered mutation orchestration
│   │       └── crossover.py        # Genetic crossover operations
│   └── infrastructure/     # External integrations
│       ├── parsing/       # Python → IR
│       ├── codegen/       # IR → Python
│       ├── llm/          # LLM clients
│       └── execution/    # Code runner with energy monitoring
├── tests/                  # Comprehensive test suite
└── examples/              # Example code and benchmarks
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

- **[Documentation Hub](docs/README.md)** - Central entry point for all docs
- **[Installation](docs/SETUP.md)** - Setup guide
- **[CLI Reference](docs/CLI.md)** - Command line usage
- **[Architecture](docs/ARCHITECTURE.md)** - System design and IR details
- **[Mutators](docs/MUTATORS.md)** - Mutation strategies explained

## 🔬 Key Concepts

### Hierarchical Mutation Layers

HEDGE implements a **4-layer hierarchical mutation system** that operates from high-level algorithmic optimizations down to low-level micro-optimizations:

#### 🧠 **Semantic Layer** (Highest Level)
- **AlgorithmicIntentMutator**: Algorithm selection and Big-O complexity optimization
- **ProgramIntentMutator**: Logic simplification and control flow optimization
- *Requires LLM API key for advanced semantic analysis*

#### 📊 **Algorithmic Layer**
- **DataStructureOptimizer**: List→Set conversion, access pattern optimization
- **ComplexityReducer**: Nested loop reduction, mathematical optimizations

#### 🐍 **Syntactic Layer**
- **PythonicIdiomOptimizer**: Comprehensions, built-ins, iterator optimization
- **CodePatternOptimizer**: LLM-based pattern improvements and idiom suggestions

#### ⚡ **Micro Layer** (Lowest Level)
- **ConstantOptimizer**: Constant folding, propagation, arithmetic simplification
- **DeadCodeEliminator**: Unreachable code removal, unused variable elimination
- **LoopMicroOptimizer**: Small loop unrolling, strength reduction, invariant motion

**Total**: 9 mutators with 34+ optimization strategies across 4 abstraction layers

### IR-Only Mutations
All code transformations operate on a strict Intermediate Representation (IR), ensuring type safety and preventing string-based code manipulation errors.

### Multi-Objective Optimization
HEDGE optimizes for both energy consumption and execution time, maintaining a Pareto front of non-dominated solutions.

### Context-Aware Transformations
Mutation context tracks symbol tables and data dependencies, ensuring transformations preserve program semantics.
