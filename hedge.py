#!/usr/bin/env python3
"""
HEDGE - Hierarchical Evolutionary Darwin-Green Engine
======================================================

A state-of-the-art IR-only code optimization system using evolutionary strategies.

Usage:
    hedge optimize <target> <tests> [options]
    hedge analyze <code> [options]
    hedge visualize <results_dir>
    hedge --help
"""
import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try to import rich for better CLI output
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

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
from src.utils.logging_config import setup_logging, silence_noisy_libraries

def print_banner():
    """Print HEDGE banner."""
    if RICH_AVAILABLE:
        banner = """
╦ ╦╔═╗╔╦╗╔═╗╔═╗
╠═╣║╣  ║║║ ╦║╣ 
╩ ╩╚═╝═╩╝╚═╝╚═╝
Hierarchical Evolutionary Darwin-Green Engine
IR-Only Optimization System | v2.0
"""
        console.print(Panel(banner, style="bold cyan", border_style="cyan"))
    else:
        print("="*60)
        print(" HEDGE - Hierarchical Evolutionary Darwin-Green Engine")
        print(" IR-Only Optimization System | v2.0")
        print("="*60)

def cmd_optimize(args):
    """Execute optimization command."""
    if RICH_AVAILABLE:
        console.print("\n[bold cyan]Starting Optimization[/bold cyan]\n")
    else:
        print("\nStarting Optimization\n")
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    if args.experiment_dir:
        log_file = Path(args.experiment_dir) / "hedge.log"
    else:
        log_file = None
    
    if RICH_AVAILABLE:
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(message)s",
            handlers=[RichHandler(console=console, rich_tracebacks=True)]
        )
        # Silence noisy third-party libraries when using verbose/DEBUG mode
        if args.verbose:
            silence_noisy_libraries()
    else:
        setup_logging(log_level, log_file, args.verbose)
    
    logger = logging.getLogger(__name__)
    
    # Read target code
    logger.info(f"Loading target: {args.target}")
    with open(args.target, "r") as f:
        initial_code = f.read()
    
    # Read test code
    logger.info(f"Loading tests: {args.tests}")
    with open(args.tests, "r") as f:
        test_code = f.read()
    
    # Setup experiment directory
    if args.experiment_dir:
        experiment_dir = Path(args.experiment_dir)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment_dir = Path(f"experiments/run_{timestamp}")
    
    experiment_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Experiment directory: {experiment_dir}")
    
    # Save configuration
    config = vars(args)
    with open(experiment_dir / "config.json", 'w') as f:
        json.dump(config, f, indent=2, default=str)
    
    # Initialize components with progress
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Initializing components...", total=None)
            
            runner = GreenGymRunner(timeout_seconds=args.timeout)
            progress.update(task, description="[green]✓[/green] Green Gym runner initialized")
            
            mutators = _setup_mutators(args, progress, task)
            progress.update(task, description="[green]✓[/green] All mutators initialized")
    else:
        print("Initializing components...")
        runner = GreenGymRunner(timeout_seconds=args.timeout)
        print("✓ Green Gym runner initialized")
        mutators = _setup_mutators(args)
        print("✓ All mutators initialized")
    
    # Create engine
    engine = EvolutionaryEngine(
        mutators=mutators,
        runner=runner,
        generations=args.generations,
        population_size=args.population_size,
        experiment_dir=experiment_dir,
        save_ir_snapshots=args.save_ir
    )
    
    # Run optimization
    logger.info(f"\nStarting optimization with {args.generations} generations")
    logger.info(f"Mutators: {[m.__class__.__name__ for m in mutators]}\n")
    
    start_time = datetime.now()
    
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Optimizing...", total=args.generations)
            
            # Run optimization (would need to modify engine to support progress callbacks)
            solutions = engine.optimize(initial_code, test_code)
            
            progress.update(task, completed=args.generations)
    else:
        solutions = engine.optimize(initial_code, test_code)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Display results
    _display_results(solutions, engine, duration, experiment_dir, args)
    
    # Generate visualizations if requested
    if args.visualize:
        logger.info("\nGenerating visualizations...")
        visualizer = ResultVisualizer(experiment_dir)
        visualizer.generate_all()
        
        if RICH_AVAILABLE:
            console.print("\n[bold green]✓[/bold green] Visualizations generated!")
            console.print(f"  └─ View report at: [link]file://{experiment_dir}/visualizations/report.html[/link]")
    
    return 0

def _setup_mutators(args, progress=None, task=None):
    """Set up mutators based on arguments."""
    mutators = []
    
    # Structural mutator (always enabled)
    mutators.append(StructuralMutator(use_context=not args.no_context))
    if progress:
        progress.update(task, description="[green]✓[/green] Structural mutator enabled")
    
    # Semantic mutator
    if args.enable_semantic:
        api_key = os.getenv(f"{args.llm_provider.upper()}_API_KEY")
        if api_key:
            llm = create_llm_client(args.llm_provider, api_key, args.llm_model)
            mutators.append(SemanticMutator(llm))
            if progress:
                progress.update(task, description=f"[green]✓[/green] Semantic mutator enabled ({args.llm_provider})")
        else:
            logging.warning(f"API key not found for {args.llm_provider}")
    
    # Advanced mutators
    if args.enable_advanced:
        mutators.extend([
            ConstantFoldingMutator(),
            DeadCodeEliminationMutator()
        ])
        if progress:
            progress.update(task, description="[green]✓[/green] Advanced mutators enabled")
    
    return mutators

def _display_results(solutions, engine, duration, experiment_dir, args):
    """Display optimization results."""
    codegen = PythonCodeGenerator()
    metrics_collector = IRMetricsCollector()
    
    if RICH_AVAILABLE:
        # Create results table
        console.print("\n")
        console.print(Panel.fit(
            f"[bold green]Optimization Complete![/bold green]\n\n"
            f"Time: {duration:.2f}s\n"
            f"Solutions: {len(solutions)}\n"
            f"Success Rate: {engine.statistics.success_rate:.1f}%\n"
            f"Cache Hits: {engine.statistics.cache_hits}",
            border_style="green"
        ))
        
        # Results table
        table = Table(title="\nPareto-Optimal Solutions", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim")
        table.add_column("Mutation Type")
        table.add_column("Energy (J)", justify="right")
        table.add_column("Time (s)", justify="right")
        table.add_column("Complexity", justify="right")
        
        results = []
        for i, sol in enumerate(solutions):
            code = codegen.generate(sol.ir)
            ir_metrics = metrics_collector.collect(sol.ir)
            
            table.add_row(
                str(i+1),
                sol.mutation_type,
                f"{sol.metrics.get('energy_joules', 0):.4f}",
                f"{sol.metrics.get('duration_seconds', 0):.4f}",
                str(ir_metrics.cyclomatic_complexity)
            )
            
            results.append({
                "id": sol.variant_id,
                "metrics": sol.metrics,
                "mutation": sol.mutation_type,
                "ir_metrics": {
                    "complexity": ir_metrics.cyclomatic_complexity,
                    "nodes": ir_metrics.total_nodes,
                    "depth": ir_metrics.max_depth
                },
                "code": code
            })
        
        console.print(table)
    else:
        print("\n" + "="*60)
        print("OPTIMIZATION COMPLETE")
        print("="*60)
        print(f"Time: {duration:.2f}s")
        print(f"Solutions: {len(solutions)}")
        print(f"Success Rate: {engine.statistics.success_rate:.1f}%")
        
        results = []
        for i, sol in enumerate(solutions):
            code = codegen.generate(sol.ir)
            ir_metrics = metrics_collector.collect(sol.ir)
            print(f"\nSolution {i+1} [{sol.mutation_type}]:")
            print(f"  Energy: {sol.metrics.get('energy_joules', 0):.4f} J")
            print(f"  Time: {sol.metrics.get('duration_seconds', 0):.4f} s")
            
            results.append({
                "id": sol.variant_id,
                "metrics": sol.metrics,
                "mutation": sol.mutation_type,
                "ir_metrics": {
                    "complexity": ir_metrics.cyclomatic_complexity,
                    "nodes": ir_metrics.total_nodes,
                    "depth": ir_metrics.max_depth
                },
                "code": code
            })
    
    # Save results
    results_path = experiment_dir / "pareto_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    stats_path = experiment_dir / "statistics.json"
    with open(stats_path, 'w') as f:
        json.dump(engine.statistics.to_dict(), f, indent=2)
    
    # Save best solution
    if solutions:
        best = min(solutions, key=lambda s: s.metrics.get("energy_joules", float('inf')))
        best_code = codegen.generate(best.ir)
        
        output_path = args.target.replace(".py", "_optimized.py")
        with open(output_path, 'w') as f:
            f.write(best_code)
        
        baseline_energy = solutions[0].metrics.get('energy_joules', 1)
        improvement = ((baseline_energy - best.metrics.get('energy_joules', baseline_energy)) / baseline_energy * 100)
        
        if RICH_AVAILABLE:
            console.print(f"\n[bold green]✓[/bold green] Best solution saved: [cyan]{output_path}[/cyan]")
            if improvement > 0:
                console.print(f"  [green]↓ {improvement:.1f}% energy improvement[/green]\n")
        else:
            print(f"\n✓ Best solution saved: {output_path}")
            if improvement > 0:
                print(f"  ↓ {improvement:.1f}% energy improvement")

def cmd_analyze(args):
    """Analyze code complexity and structure."""
    from src.infrastructure.parsing.python_parser import PythonParser
    from src.domain.ir.metrics import IRMetricsCollector
    
    print_banner()
    
    with open(args.code, 'r') as f:
        code = f.read()
    
    parser = PythonParser()
    ir = parser.parse(code)
    
    collector = IRMetricsCollector()
    metrics = collector.collect(ir)
    
    if RICH_AVAILABLE:
        table = Table(title="Code Analysis", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="green")
        
        table.add_row("Total Nodes", str(metrics.total_nodes))
        table.add_row("Statements", str(metrics.total_statements))
        table.add_row("Expressions", str(metrics.total_expressions))
        table.add_row("Max Depth", str(metrics.max_depth))
        table.add_row("Cyclomatic Complexity", str(metrics.cyclomatic_complexity))
        table.add_row("Functions", str(metrics.function_count))
        table.add_row("Loops", str(metrics.loop_count))
        table.add_row("Conditionals", str(metrics.conditional_count))
        
        console.print(table)
    else:
        print("\nCode Analysis:")
        print(f"  Total Nodes: {metrics.total_nodes}")
        print(f"  Cyclomatic Complexity: {metrics.cyclomatic_complexity}")
        print(f"  Functions: {metrics.function_count}")
    
    return 0

def cmd_visualize(args):
    """Generate visualizations from results."""
    print_banner()
    
    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        return 1
    
    visualizer = ResultVisualizer(results_dir)
    visualizer.generate_all()
    
    if RICH_AVAILABLE:
        console.print(f"\n[bold green]✓[/bold green] Visualizations generated!")
        console.print(f"  View report: [link]file://{results_dir}/visualizations/report.html[/link]\n")
    else:
        print(f"\n✓ Visualizations generated at: {results_dir}/visualizations/")
    
    return 0

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="HEDGE - IR-Only Code Optimization System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic optimization
  hedge optimize fibonacci.py fibonacci_test.py
  
  # With LLM and visualizations
  hedge optimize fibonacci.py fibonacci_test.py --enable-semantic --visualize
  
  # Analyze code complexity
  hedge analyze mycode.py
  
  # Generate visualizations from existing results
  hedge visualize experiments/run_20231204_123456
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Optimize Python code')
    optimize_parser.add_argument('target', type=str, help='Target Python file to optimize')
    optimize_parser.add_argument('tests', type=str, help='Test file')
    optimize_parser.add_argument('--generations', type=int, default=5, help='Number of generations (default: 5)')
    optimize_parser.add_argument('--population-size', type=int, default=5, help='Population size (default: 5)')
    optimize_parser.add_argument('--timeout', type=int, default=20, help='Timeout for code execution (default: 20s)')
    optimize_parser.add_argument('--enable-semantic', action='store_true', help='Enable LLM-based semantic mutations')
    optimize_parser.add_argument('--enable-advanced', action='store_true', help='Enable advanced optimizations')
    optimize_parser.add_argument('--llm-provider', type=str, default='gemini', choices=['openai', 'gemini'], help='LLM provider')
    optimize_parser.add_argument('--llm-model', type=str, default=None, help='LLM model (optional)')
    optimize_parser.add_argument('--no-context', action='store_true', help='Disable context-aware mutations')
    optimize_parser.add_argument('--save-ir', action='store_true', help='Save IR snapshots')
    optimize_parser.add_argument('--experiment-dir', type=str, default=None, help='Experiment directory')
    optimize_parser.add_argument('--visualize', action='store_true', help='Generate visualizations after optimization')
    optimize_parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze code complexity')
    analyze_parser.add_argument('code', type=str, help='Python file to analyze')
    
    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Generate visualizations')
    viz_parser.add_argument('results_dir', type=str, help='Results directory')
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command is None:
        print_banner()
        parser.print_help()
        return 0
    
    # Execute command
    if args.command == 'optimize':
        print_banner()
        return cmd_optimize(args)
    elif args.command == 'analyze':
        return cmd_analyze(args)
    elif args.command == 'visualize':
        return cmd_visualize(args)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
