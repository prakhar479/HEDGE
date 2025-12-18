# EvoEval Benchmark Suite for HEDGE

This directory contains 9 difficult problems from the EvoEval benchmark, organized for optimization with HEDGE.

## Problems

| Problem ID | Function | Description |
|------------|----------|-------------|
| EvoEval_difficult_4 | `weighted_mean_absolute_deviation` | from typing import List, Tuple


def weighted_mean_absolute_... |
| EvoEval_difficult_16 | `count_distinct_characters_substrings` | def count_distinct_characters_substrings(string: str, length... |
| EvoEval_difficult_52 | `below_above_threshold` | def below_above_threshold(l: list, t1: int, t2: int, s: str)... |
| EvoEval_difficult_53 | `add_elements` | def add_elements(list1: list, list2: list, index: int):
    ... |
| EvoEval_difficult_61 | `correct_bracketing_advanced` | def correct_bracketing_advanced(brackets: str):
    """
    ... |
| EvoEval_difficult_63 | `customFibFib` | def customFibFib(n: int, startSequence: list, p: int):
    "... |
| EvoEval_difficult_66 | `advancedDigitSum` | def advancedDigitSum(s, t):
    """
    Task
    Write a fun... |
| EvoEval_difficult_79 | `decimal_to_binary` | def decimal_to_binary(decimal, padding_length):
    """You w... |
| EvoEval_difficult_90 | `next_smallest_and_largest` | def next_smallest_and_largest(lst):
    """
    You are give... |

## Quick Start

### Run a Single Problem

```bash
# Example: Run EvoEval_difficult_4 with layered system
python hedge.py optimize evoeval_benchmark/EvoEval_difficult_4/target.py \
                         evoeval_benchmark/EvoEval_difficult_4/test_target.py \
                         --level standard \
                         --generations 5 \
                         --visualize

# Advanced optimization with semantic layer (requires LLM API key)
export GEMINI_API_KEY="your-api-key"
python hedge.py optimize evoeval_benchmark/EvoEval_difficult_4/target.py \
                         evoeval_benchmark/EvoEval_difficult_4/test_target.py \
                         --level advanced \
                         --generations 10 \
                         --visualize

# Custom layer selection
python hedge.py optimize evoeval_benchmark/EvoEval_difficult_4/target.py \
                         evoeval_benchmark/EvoEval_difficult_4/test_target.py \
                         --layers algorithmic,syntactic \
                         --generations 5
```

### Run All Problems

```bash
# NOTE: The batch benchmark script needs updating for the layered system
# For now, run individual problems or use legacy mode:
python run_evoeval_benchmarks.py  # (needs updating - uses legacy system)

# Or run with legacy mode:
python hedge.py optimize <target> <tests> --legacy-mode --level advanced
```

## Structure

Each problem directory contains:
- `target.py` - The canonical solution to optimize
- `test_target.py` - Test suite with multiple test cases
- `README.md` - Problem-specific documentation

## Expected Optimizations

HEDGE will attempt to optimize these implementations through its hierarchical layers:

- **🧠 Semantic Layer**: Algorithm intent optimization (O(n²) → O(n log n), better algorithms)
- **📊 Algorithmic Layer**: Data structure improvements (List → Set for membership, complexity reduction)
- **🐍 Syntactic Layer**: Python idiom optimization (comprehensions, built-ins, patterns)
- **⚡ Micro Layer**: Low-level optimizations (constant folding, dead code elimination)

Results will show Pareto-optimal solutions balancing energy consumption and execution time, with detailed layer contribution analysis.

## Generated

This benchmark suite was auto-generated from `evoeval_difficult_entries.json`.
