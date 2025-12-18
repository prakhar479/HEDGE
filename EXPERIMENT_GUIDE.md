# HEDGE Comprehensive Experiment Guide

## Overview

This guide explains the exhaustive experiment setup for testing the HEDGE code optimizer across multiple optimization levels and complexity scenarios.

## What's Running

The comprehensive experiment suite (`run_comprehensive_experiments.py`) is currently executing **9 different optimization experiments** that showcase the full potential of HEDGE:

### Experiment Categories

#### 1. **Micro-Optimizations** (Quick, Safe)
- `fib_micro`: Fibonacci with constant folding & dead code elimination
- `formal_micro`: Formal example with micro-level optimizations

#### 2. **Standard Optimizations** (Recommended)
- `search_standard`: Linear search optimization (15 generations)
- `complex_standard`: Complex code with multiple inefficiencies (20 generations)

#### 3. **Advanced with LLM** (Semantic Layer)
- `fib_advanced`: Fibonacci with AI-powered algorithm optimization (25 generations)
- `complex_advanced`: Full advanced optimization with semantic layer (30 generations)

#### 4. **Aggressive Long-Running** (Maximum Optimization)
- `complex_aggressive_long`: 50 generations of aggressive optimization
- `fib_aggressive_long`: 40 generations on Fibonacci

#### 5. **Custom Layer Combinations**
- `complex_custom_algo_micro`: Algorithmic + Micro layers only (20 generations)

## Experiment Structure

Each experiment produces:
```
experiments/comprehensive_TIMESTAMP/
├── fib_micro/
│   ├── config.json              # Experiment configuration
│   ├── pareto_results.json      # Pareto-optimal solutions
│   ├── statistics.json          # Mutation statistics
│   ├── stdout.log               # Console output
│   ├── stderr.log               # Error output
│   └── visualizations/          # Charts and HTML report
├── complex_standard/
│   └── ...
└── suite_summary.json           # Overall summary
```

## Monitoring Progress

### Check Current Status
```bash
# View the process output
python -c "import subprocess; subprocess.run(['tail', '-f', 'comprehensive_run.log'])"
```

### List Running Processes
```bash
ps aux | grep python
```

## After Completion

### 1. Aggregate Results
Once all experiments complete, run the aggregation script:

```bash
python aggregate_results.py experiments/comprehensive_TIMESTAMP/
```

This generates:
- **Comparison charts** across all experiments
- **Comprehensive HTML report** with all metrics
- **Energy improvement analysis**
- **Success rate comparisons**

### 2. View Results

The aggregated report will be at:
```
experiments/comprehensive_TIMESTAMP/aggregated/comprehensive_report.html
```

Open it in your browser to see:
- Energy improvement percentages
- Mutation success rates
- Pareto front sizes
- Energy vs Time scatter plots
- Individual experiment details

## Key Metrics to Analyze

### Energy Efficiency
- **Baseline Energy**: Initial energy consumption
- **Optimized Energy**: Best solution energy
- **Improvement %**: (Baseline - Best) / Baseline × 100

### Optimization Quality
- **Pareto Solutions**: Number of non-dominated solutions found
- **Success Rate**: Percentage of valid mutations
- **Cache Hits**: Reused evaluations (efficiency indicator)

### Complexity Analysis
- **Cyclomatic Complexity**: Code complexity metric
- **IR Nodes**: Intermediate representation size
- **Max Depth**: AST depth

## Example Optimizations

### Fibonacci (Recursive → Iterative/Memoized)
```python
# Before (O(2^n))
def fib_recursive(n):
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)

# After (O(n) or O(1) with memoization)
# HEDGE can discover iterative or memoized versions
```

### Complex Data Processing
```python
# Before: Bubble sort O(n²), manual loops
def process_data(numbers):
    # Bubble sort
    for i in range(len(numbers)):
        for j in range(len(numbers)-i-1):
            if numbers[j] > numbers[j+1]:
                numbers[j], numbers[j+1] = numbers[j+1], numbers[j]
    # Manual filtering
    result = []
    for x in numbers:
        if x % 2 == 0:
            result.append(x * 3)
    return result

# After: Built-in sort O(n log n), comprehensions
def process_data(numbers):
    return [x * 3 for x in sorted(numbers) if x % 2 == 0]
```

## Optimization Layers

### Micro Layer (Fastest)
- Constant folding: `24 * 60 * 60` → `86400`
- Dead code elimination: Remove unreachable code
- Strength reduction: `x ** 2` → `x * x`

### Syntactic Layer
- List comprehensions
- Built-in functions (map, filter, sum)
- Python idioms

### Algorithmic Layer
- Data structure optimization (list → set)
- Complexity reduction (nested loops)
- Algorithm selection

### Semantic Layer (Most Powerful)
- Algorithm intent recognition
- Big-O complexity optimization
- Logic simplification

## Expected Runtime

- **Micro experiments**: ~1-2 minutes each
- **Standard experiments**: ~3-5 minutes each
- **Advanced experiments**: ~5-10 minutes each
- **Aggressive experiments**: ~10-20 minutes each

**Total estimated time**: 60-90 minutes for all 9 experiments

## Troubleshooting

### Experiment Fails
- Check `stderr.log` in the experiment directory
- Verify API key is set in `.env` for advanced/aggressive experiments
- Ensure test files exist and are valid

### Timeout Issues
- Increase timeout in `run_comprehensive_experiments.py`
- Reduce generations for long-running experiments
- Check system resources (CPU, memory)

### No Improvements Found
- Some code may already be optimal
- Try different optimization levels
- Check mutation statistics for insights

## Next Steps

1. **Wait for completion** (~60-90 minutes)
2. **Run aggregation**: `python aggregate_results.py experiments/comprehensive_TIMESTAMP/`
3. **Analyze results**: Open the HTML report
4. **Compare optimizations**: Review energy improvements
5. **Examine code**: Check `*_optimized.py` files

## Advanced Usage

### Custom Experiments

Add your own experiments to `run_comprehensive_experiments.py`:

```python
{
    "name": "my_custom_experiment",
    "target": "my_code.py",
    "tests": "test_my_code.py",
    "level": "advanced",
    "generations": 25,
    "description": "My custom optimization"
}
```

### Specific Layer Testing

Test individual layers:
```bash
python hedge.py optimize code.py tests.py --layers semantic
python hedge.py optimize code.py tests.py --layers algorithmic,micro
```

### Exclude Specific Mutators

```bash
python hedge.py optimize code.py tests.py --exclude-mutators "ExternalLibraryMutator,SemanticMutator"
```

## Resources

- **Documentation**: `docs/README.md`
- **CLI Reference**: `docs/CLI.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Mutators**: `docs/MUTATORS.md`

## Citation

If you use HEDGE in your research, please cite:
```
HEDGE - Hierarchical Evolutionary Darwin-Green Engine
A state-of-the-art IR-only code optimization system
```
