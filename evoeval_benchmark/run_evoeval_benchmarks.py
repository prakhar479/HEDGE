#!/usr/bin/env python3
"""
Run HEDGE optimization on all EvoEval benchmark problems.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


def run_benchmark(problem_dir: Path, generations: int = 5, layers: list = None, visualize: bool = False):
    """Run HEDGE on a single benchmark problem."""

    if layers is None:
        layers = ['L1', 'L2']

    target_file = problem_dir / "target.py"
    test_file = problem_dir / "test_target.py"

    if not target_file.exists() or not test_file.exists():
        print(f"  ✗ Missing files in {problem_dir}")
        return False

    # Build command
    cmd = [
        "python", "main.py",
        "--target", str(target_file),
        "--tests", str(test_file),
        "--generations", str(generations),
        "--layers", *layers
    ]

    if visualize:
        cmd.append("--visualize")

    print(f"\n{'='*60}")
    print(f"Running: {problem_dir.name}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, capture_output=False, text=True, timeout=600)
        success = result.returncode == 0
        return success
    except subprocess.TimeoutExpired:
        print(f"  ⚠ Timeout after 10 minutes")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def run_all_benchmarks(benchmark_dir: str = "evoeval_benchmark",
                       generations: int = 5,
                       layers: list = None,
                       visualize: bool = False,
                       problem_filter: str = None):
    """Run HEDGE on all benchmark problems."""

    base_path = Path(benchmark_dir)

    if not base_path.exists():
        print(f"Error: Benchmark directory '{benchmark_dir}' not found")
        print(f"Run 'python extract_evoeval.py' first to create the benchmarks")
        sys.exit(1)

    # Find all problem directories
    problem_dirs = sorted([d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("EvoEval")])

    # Apply filter if specified
    if problem_filter:
        problem_dirs = [d for d in problem_dirs if problem_filter.lower() in d.name.lower()]

    if not problem_dirs:
        print(f"No problems found matching filter: {problem_filter}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"HEDGE EvoEval Benchmark Suite")
    print(f"{'='*60}")
    print(f"Total problems: {len(problem_dirs)}")
    print(f"Generations: {generations}")
    print(f"Layers: {', '.join(layers or ['L1', 'L2'])}")
    print(f"Visualize: {visualize}")
    if problem_filter:
        print(f"Filter: {problem_filter}")
    print(f"{'='*60}\n")

    results = {}
    start_time = datetime.now()

    for i, problem_dir in enumerate(problem_dirs, 1):
        print(f"\n[{i}/{len(problem_dirs)}] Processing {problem_dir.name}...")

        success = run_benchmark(problem_dir, generations, layers, visualize)
        results[problem_dir.name] = {
            "success": success,
            "timestamp": datetime.now().isoformat()
        }

        if success:
            print(f"  ✓ {problem_dir.name} completed successfully")
        else:
            print(f"  ✗ {problem_dir.name} failed")

    end_time = datetime.now()
    duration = end_time - start_time

    # Print summary
    print(f"\n{'='*60}")
    print(f"BENCHMARK SUMMARY")
    print(f"{'='*60}")
    print(f"Total problems: {len(problem_dirs)}")
    print(f"Successful: {sum(1 for r in results.values() if r['success'])}")
    print(f"Failed: {sum(1 for r in results.values() if not r['success'])}")
    print(f"Duration: {duration}")
    print(f"{'='*60}\n")

    # Save results
    results_file = f"evoeval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            "summary": {
                "total": len(problem_dirs),
                "successful": sum(1 for r in results.values() if r['success']),
                "failed": sum(1 for r in results.values() if not r['success']),
                "duration_seconds": duration.total_seconds(),
                "generations": generations,
                "layers": layers or ['L1', 'L2']
            },
            "results": results
        }, f, indent=2)

    print(f"Results saved to: {results_file}")

    # List failed problems
    failed = [name for name, data in results.items() if not data['success']]
    if failed:
        print(f"\nFailed problems:")
        for name in failed:
            print(f"  - {name}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run HEDGE on EvoEval benchmark suite")
    parser.add_argument("--generations", "-g", type=int, default=5,
                        help="Number of generations (default: 5)")
    parser.add_argument("--layers", "-l", nargs='+', default=['L1', 'L2'],
                        choices=['L1', 'L2'],
                        help="Optimization layers (default: L1 L2)")
    parser.add_argument("--visualize", "-v", action='store_true',
                        help="Generate visualizations")
    parser.add_argument("--filter", "-f", type=str,
                        help="Filter problems by name (e.g., 'difficult_4')")
    parser.add_argument("--benchmark-dir", "-d", type=str, default="evoeval_benchmark",
                        help="Benchmark directory (default: evoeval_benchmark)")

    args = parser.parse_args()

    run_all_benchmarks(
        benchmark_dir=args.benchmark_dir,
        generations=args.generations,
        layers=args.layers,
        visualize=args.visualize,
        problem_filter=args.filter
    )
