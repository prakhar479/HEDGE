#!/usr/bin/env python3
"""
Run HEDGE optimization on all EvoEval benchmark problems.
Compatible with HEDGE v2.0 component interface.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import HEDGE components
from src.application.engine.evolution import EvolutionaryEngine
from src.application.mutators.structural import StructuralMutator
from src.application.mutators.semantic import SemanticMutator
from src.application.mutators.advanced import (
    ConstantFoldingMutator,
    DeadCodeEliminationMutator
)
from src.infrastructure.execution.runner import GreenGymRunner
from src.infrastructure.llm.client import create_llm_client
from src.infrastructure.codegen.python_codegen import PythonCodeGenerator
from src.domain.ir.metrics import IRMetricsCollector
from src.utils.visualizer import ResultVisualizer
from src.utils.logging_config import setup_logging

def setup_mutators(args) -> list:
    """Set up mutators based on arguments."""
    mutators = []
    
    # Structural mutator (always enabled)
    mutators.append(StructuralMutator(use_context=not args.no_context))
    
    # Semantic mutator
    if args.enable_semantic:
        api_key = os.getenv(f"{args.llm_provider.upper()}_API_KEY")
        if api_key:
            llm = create_llm_client(args.llm_provider, api_key, args.llm_model)
            mutators.append(SemanticMutator(llm))
        else:
            print(f"Warning: API key not found for {args.llm_provider}, skipping SemanticMutator")
    
    # Advanced mutators
    if args.enable_advanced:
        mutators.extend([
            ConstantFoldingMutator(),
            DeadCodeEliminationMutator()
        ])
    
    return mutators

def run_benchmark(problem_dir: Path, 
                 args: argparse.Namespace,
                 run_logger: logging.Logger) -> Dict[str, Any]:
    """Run HEDGE on a single benchmark problem."""
    
    target_file = problem_dir / "target.py"
    test_file = problem_dir / "test_target.py"

    if not target_file.exists() or not test_file.exists():
        run_logger.error(f"Missing files in {problem_dir}")
        return {"success": False, "error": "Missing target or test files"}

    run_logger.info(f"Running benchmark: {problem_dir.name}")

    # Read code
    with open(target_file, "r") as f:
        initial_code = f.read()
    with open(test_file, "r") as f:
        test_code = f.read()

    # Patch test code to import from 'candidate' instead of 'target'
    # GreenGymRunner saves the code as 'candidate.py'
    test_code = test_code.replace("from target", "from candidate")
    test_code = test_code.replace("import target", "import candidate")

    # Setup experiment directory for this problem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_dir = problem_dir / "results" / f"run_{timestamp}"
    experiment_dir.mkdir(parents=True, exist_ok=True)

    # Initialize components
    runner = GreenGymRunner(timeout_seconds=args.timeout)
    mutators = setup_mutators(args)
    
    engine = EvolutionaryEngine(
        mutators=mutators,
        runner=runner,
        generations=args.generations,
        population_size=args.population_size,
        experiment_dir=experiment_dir,
        save_ir_snapshots=args.save_ir
    )

    try:
        start_time = datetime.now()
        solutions = engine.optimize(initial_code, test_code)
        duration = (datetime.now() - start_time).total_seconds()
        
        # Analyze results
        success = len(solutions) > 0
        best_solution = None
        improvement = 0.0
        
        if success:
            best_solution = min(solutions, key=lambda s: s.metrics.get("energy_joules", float('inf')))
            baseline_energy = solutions[0].metrics.get('energy_joules', 1)
            if baseline_energy > 0:
                current_energy = best_solution.metrics.get('energy_joules', baseline_energy)
                improvement = ((baseline_energy - current_energy) / baseline_energy * 100)
            
            # Save best code
            codegen = PythonCodeGenerator()
            best_code = codegen.generate(best_solution.ir)
            with open(experiment_dir / "best_optimized.py", 'w') as f:
                f.write(best_code)

        # Generate visualizations if requested
        if args.visualize:
            visualizer = ResultVisualizer(experiment_dir)
            visualizer.generate_all()

        return {
            "success": success,
            "problem": problem_dir.name,
            "duration_seconds": duration,
            "generations": args.generations,
            "solutions_found": len(solutions),
            "best_improvement_pct": improvement,
            "best_energy": best_solution.metrics.get("energy_joules") if best_solution else None,
            "experiment_dir": str(experiment_dir)
        }

    except Exception as e:
        run_logger.exception(f"Error running benchmark {problem_dir.name}")
        return {"success": False, "error": str(e)}

def run_all_benchmarks(args):
    """Run HEDGE on all benchmark problems."""
    
    benchmark_dir = Path(args.benchmark_dir)
    if not benchmark_dir.exists():
        print(f"Error: Benchmark directory '{args.benchmark_dir}' not found")
        sys.exit(1)

    # Find problems
    problem_dirs = sorted([d for d in benchmark_dir.iterdir() if d.is_dir() and d.name.startswith("EvoEval")])
    
    if args.filter:
        problem_dirs = [d for d in problem_dirs if args.filter.lower() in d.name.lower()]
    
    if not problem_dirs:
        print(f"No problems found matching filter.")
        sys.exit(1)

    print(f"Found {len(problem_dirs)} benchmarks to run.")
    
    # Setup logging
    log_file = f"benchmark_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    setup_logging("INFO", Path(log_file), verbose=args.verbose)
    logger = logging.getLogger("BenchmarkRunner")

    results = {}
    overall_start = datetime.now()

    for i, p_dir in enumerate(problem_dirs, 1):
        print(f"\n[{i}/{len(problem_dirs)}] Processing {p_dir.name}...")
        res = run_benchmark(p_dir, args, logger)
        results[p_dir.name] = res
        
        status = "✓" if res['success'] else "✗"
        if res['success']:
             print(f"  {status} Success! Improvement: {res['best_improvement_pct']:.2f}%")
        else:
             print(f"  {status} Failed: {res.get('error', 'Unknown error')}")

    duration = datetime.now() - overall_start
    
    # Save aggregate results
    summary = {
        "summary": {
            "total": len(problem_dirs),
            "successful": sum(1 for r in results.values() if r['success']),
            "failed": sum(1 for r in results.values() if not r['success']),
            "total_duration": duration.total_seconds(),
            "config": vars(args)
        },
        "results": results
    }
    
    results_file = f"evoeval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
        
    print(f"\nAll benchmarks completed in {duration}. Results saved to {results_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run HEDGE on EvoEval benchmark suite")
    
    # Selection arguments
    parser.add_argument("--benchmark-dir", "-d", type=str, default="evoeval_benchmark",
                        help="Benchmark directory")
    parser.add_argument("--filter", "-f", type=str, help="Filter problems by name")
    
    # Engine arguments (matching hedge.py)
    parser.add_argument("--generations", "-g", type=int, default=5, help="Number of generations")
    parser.add_argument("--population-size", "-p", type=int, default=5, help="Population size")
    parser.add_argument("--timeout", type=int, default=20, help="Execution timeout (s)")
    
    # Mutator arguments
    parser.add_argument('--enable-semantic', action='store_true', help='Enable LLM-based semantic mutations')
    parser.add_argument('--enable-advanced', action='store_true', help='Enable advanced optimizations')
    parser.add_argument('--llm-provider', type=str, default='gemini', choices=['openai', 'gemini'], help='LLM provider')
    parser.add_argument('--llm-model', type=str, default=None, help='LLM model')
    parser.add_argument('--no-context', action='store_true', help='Disable context-aware mutations')
    
    # Output arguments
    parser.add_argument('--save-ir', action='store_true', help='Save IR snapshots')
    parser.add_argument("--visualize", "-v", action='store_true', help="Generate visualizations")
    parser.add_argument("--verbose", action='store_true', help="Verbose logging")

    args = parser.parse_args()
    run_all_benchmarks(args)
