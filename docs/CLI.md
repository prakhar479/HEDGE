# HEDGE CLI Reference

Complete reference for the HEDGE command-line interface with layered mutation system.

## Installation

### Install Dependencies
```bash
pip install -r requirements.txt

# Optional: Enhanced UI and visualizations
pip install rich matplotlib
```

### Make Executable (Unix/Linux/Mac)
```bash
chmod +x hedge.py
```

## Quick Start

### Basic Usage
```bash
# Micro-optimizations only (constant folding, dead code elimination)
python3 hedge.py optimize examples/target.py examples/test_target.py --level micro

# Standard layered optimization (recommended)
python3 hedge.py optimize examples/target.py examples/test_target.py --level standard

# Advanced with semantic layer (requires LLM API key)
export GEMINI_API_KEY="your-api-key"
python3 hedge.py optimize examples/target.py examples/test_target.py --level advanced

# Custom layer selection
python3 hedge.py optimize examples/target.py examples/test_target.py --layers micro,algorithmic
```

### Advanced Usage
```bash
# Deep optimization with visualization
python3 hedge.py optimize fibonacci.py fibonacci_test.py \
  --level advanced \
  --generations 15 \
  --visualize \
  --verbose

# Legacy mode (original mutator system)
python3 hedge.py optimize code.py tests.py --legacy-mode --level advanced

# Custom experiment directory
python3 hedge.py optimize fibonacci.py fibonacci_test.py \
  --experiment-dir my_experiment \
  --save-ir
```

### Other Commands
```bash
# Analyze code complexity
python3 hedge.py analyze mycode.py

# Generate visualizations from existing results
python3 hedge.py visualize experiments/run_20231204_123456

# List available mutators and layers
python3 hedge.py list-mutators
```

## Commands

### `optimize`
Optimize Python code using hierarchical evolutionary strategies.

**Arguments:**
- `target` - Python file to optimize (required)
- `tests` - Test file for validation (required)

**Optimization Levels:**
- `--level micro` - Micro-optimizations only (constant folding, dead code elimination)
- `--level basic` - Micro + syntactic optimizations (Python idioms, patterns)
- `--level standard` - Basic + algorithmic optimizations (data structures, complexity)
- `--level advanced` - Standard + semantic optimizations (algorithm intent, requires LLM)
- `--level aggressive` - All layers enabled with maximum optimization

**Layer Control:**
- `--layers LAYERS` - Comma-separated list of specific layers: semantic,algorithmic,syntactic,micro
- `--legacy-mode` - Use original mutator system instead of layered approach
- `--exclude-mutators LIST` - Exclude specific mutator classes (e.g., "ConstantOptimizer,DeadCodeEliminator")

**Evolution Options:**
- `--generations N` - Number of evolutionary generations (default: 5)
- `--population-size N` - Population size (default: 10)
- `--timeout N` - Execution timeout in seconds (default: 30)

**LLM Configuration:**
- `--llm-provider {openai,gemini}` - LLM provider for semantic layer (default: gemini)
- `--llm-model MODEL` - Custom LLM model name

**Output Options:**
- `--save-ir` - Save IR snapshots for debugging
- `--experiment-dir DIR` - Custom experiment directory
- `--visualize` - Generate visualizations after optimization
- `--verbose` - Detailed logging with layer statistics

**Output:**
- Pareto-optimal solutions
- Best solution saved to `<target>_optimized.py`
- Experiment results in `experiments/` or custom directory
- Visualizations (if `--visualize` is used)

### `analyze`
Analyze code complexity and structure with layer-aware metrics.

**Arguments:**
- `code` - Python file to analyze (required)

**Output:**
- IR metrics (nodes, complexity, depth)
- Code structure statistics
- Layer-specific optimization opportunities
- Complexity analysis per abstraction level

### `visualize`
Generate comprehensive visualizations from optimization results.

**Arguments:**
- `results_dir` - Directory containing experiment results (required)

**Output:**
- Pareto front plot (energy vs execution time)
- Evolution progress charts with layer statistics
- Mutation effectiveness by layer and strategy
- Layer contribution analysis
- Metrics comparison charts
- Interactive HTML report with layer breakdown

### `list-mutators`
List all available mutators organized by layer.

**Output:**
- Mutators grouped by layer (Semantic, Algorithmic, Syntactic, Micro)
- Available strategies for each mutator
- Layer dependencies and requirements

## Features

### Rich Console Output  
When `rich` is installed, HEDGE provides:
- 🎨 Colored output with syntax highlighting
- 📊 Beautiful tables for results
- ⏳ Progress bars for long operations
- 🎯 Panels and formatted displays

### Comprehensive Logging
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- Detailed operation tracking
- Performance metrics
- Error reporting with context

### Visualization Suite
- **Pareto Front**: Energy vs Time trade-off visualization
- **Evolution Progress**: Statistics over generations
- **Mutation Effectiveness**: Strategy distribution analysis
- **Metrics Comparison**: Baseline vs best solution
- **HTML Report**: Interactive report with all visualizations

### Context-Aware Mutations
- Symbol table tracking
- Dependency analysis
- Safe transformations only

## Examples

### Quick Start
```bash
# Optimize a simple function
python3 hedge.py optimize examples/fibonacci.py examples/fibonacci_test.py

# Analyze the optimized result
python3 hedge.py analyze examples/fibonacci_optimized.py
```

### Advanced Optimization
```bash
export GEMINI_API_KEY="your-api-key"

python3 hedge.py optimize mycode.py mycode_test.py \
  --level aggressive \
  --generations 20 \
  --llm-provider gemini \
  --save-ir \
  --visualize \
  --verbose \
  --experiment-dir experiments/advanced_run
```

### Visualization Only
```bash
# Generate visualizations from existing results
python3 hedge.py visualize experiments/run_20231204_123456

# View the HTML report
open experiments/run_20231204_123456/visualizations/report.html
```

## Output Structure

```
experiments/run_TIMESTAMP/
├── config.json                    # Experiment configuration
├── hedge.log                      # Detailed logs
├── pareto_results.json           # All Pareto solutions
├── statistics.json               # Mutation statistics
├── ir_snapshots/                 # IR at each generation (if --save-ir)
└── visualizations/
    ├── pareto_front.png
    ├── evolution_progress.png
    ├── mutation_effectiveness.png
    ├── metrics_comparison.png
    └── report.html               # Interactive HTML report
```

## Tips

1. **Start Simple**: Begin with basic optimization, then add features
2. **Use Visualizations**: Always use `--visualize` to understand results
3. **Save IR**: Use `--save-ir` for debugging mutations
4. **Verbose Mode**: Use `--verbose` when troubleshooting
5. **LLM API Keys**: Set environment variables for LLM providers

## Environment Variables

```bash
# For OpenAI
export OPENAI_API_KEY="sk-..."

# For Gemini
export GEMINI_API_KEY="..."
```

## Troubleshooting

### No visualizations generated
- Install matplotlib: `pip install matplotlib`

### No rich console output
- Install rich: `pip install rich`

### LLM mutations not working
- Check API key is set
- Verify API key has proper permissions
- Try different model with `--llm-model`

### Tests failing
- Ensure test file follows expected format
- Check timeout is sufficient with `--timeout`
