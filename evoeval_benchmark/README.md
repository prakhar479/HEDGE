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
# Example: Run EvoEval_difficult_4
python main.py --target evoeval_benchmark/EvoEval_difficult_4/target.py \
               --tests evoeval_benchmark/EvoEval_difficult_4/test_target.py \
               --generations 5 \
               --layers L1 L2 \
               --visualize
```

### Run All Problems

```bash
python run_evoeval_benchmarks.py
```

## Structure

Each problem directory contains:
- `target.py` - The canonical solution to optimize
- `test_target.py` - Test suite with multiple test cases
- `README.md` - Problem-specific documentation

## Expected Optimizations

HEDGE will attempt to optimize these implementations through:
- **L1 (Intent)**: Algorithmic improvements (e.g., O(n²) → O(n log n))
- **L2 (Syntax)**: Code-level optimizations (list comprehensions, library usage, etc.)

Results will show Pareto-optimal solutions balancing energy consumption and execution time.

## Generated

This benchmark suite was auto-generated from `evoeval_difficult_entries.json`.
