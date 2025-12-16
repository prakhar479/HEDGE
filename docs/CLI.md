# HEDGE CLI Interface

## Overview
HEDGE now has a single, unified CLI interface with comprehensive features and beautiful output.

## Installation

### Install Dependencies
```bash
pip install matplotlib rich pydantic
```

### Make Executable (Unix/Linux/Mac)
```bash
chmod +x hedge.py
```

## Usage

### 1. Optimize Code
```bash
# Basic optimization (Fast, no LLM)
python3 hedge.py optimize fibonacci.py fibonacci_test.py --level basic

# Standard optimization (Balanced, uses LLM)
python3 hedge.py optimize fibonacci.py fibonacci_test.py --level standard

# Deep optimization with visualization
python3 hedge.py optimize fibonacci.py fibonacci_test.py \
  --level advanced \
  --generations 10 \
  --visualize \
  --verbose

# Custom experiment directory
python3 hedge.py optimize fibonacci.py fibonacci_test.py \
  --experiment-dir my_experiment \
  --save-ir
```

### 2. Analyze Code Complexity
```bash
python3 hedge.py analyze mycode.py
```

### 3. Generate Visualizations
```bash
python3 hedge.py visualize experiments/run_20231204_123456
```

## Commands

### `optimize`
Optimize Python code using evolutionary strategies.

**Arguments:**
- `target` - Python file to optimize (required)
- `tests` - Test file for validation (required)

**Options:**
- `--level {basic,standard,advanced,aggressive}` - Optimization level (default: standard)
  - `basic`: Structural only (Fast, No LLM)
  - `standard`: Structural + Syntactic (Balanced, LLM)
  - `advanced`: Standard + Semantic (Deep, LLM StdLib)
  - `aggressive`: All + External Libraries (Unsafe)
- `--generations N` - Number of generations (default: 5)
- `--population-size N` - Population size (default: 5)
- `--timeout N` - Execution timeout in seconds (default: 20)
- `--llm-provider {openai,gemini}` - LLM provider (default: gemini)
- `--llm-model MODEL` - Custom LLM model
- `--no-context` - Disable context-aware mutations
- `--save-ir` - Save IR snapshots
- `--experiment-dir DIR` - Custom experiment directory
- `--visualize` - Generate visualizations after optimization
- `--verbose` - Verbose logging

**Output:**
- Pareto-optimal solutions
- Best solution saved to `<target>_optimized.py`
- Experiment results in `experiments/` or custom directory
- Visualizations (if `--visualize` is used)

### `analyze`
Analyze code complexity and structure.

**Arguments:**
- `code` - Python file to analyze (required)

**Output:**
- IR metrics (nodes, complexity, depth)
- Code structure statistics

### `visualize`
Generate comprehensive visualizations from optimization results.

**Arguments:**
- `results_dir` - Directory containing experiment results (required)

**Output:**
- Pareto front plot
- Evolution progress charts
- Mutation effectiveness graphs
- Metrics comparison charts
- Interactive HTML report

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
