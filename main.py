import argparse
import logging
import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.green_gym.runner import CodeRunner
from src.green_gym.monitor import EnergyMonitor
from src.mutator.simple import SimpleMutator
from src.mutator.robust import RobustMutator
from src.mutator.formal import FormalMutator
from src.mutator.llm_mutator import LLMMutator
from src.core.llm import get_llm_client
from src.core.abstraction import AbstractionManager
from src.core.engine import EvolutionaryEngine
from src.utils.logging import ExperimentLogger
from src.utils.visualizer import ExperimentVisualizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="HEDGE: Hierarchical Evolutionary Darwin-Green Engine")
    parser.add_argument("--target", type=str, required=True, help="Path to the target python file to optimize")
    parser.add_argument("--tests", type=str, required=True, help="Path to the test file")
    parser.add_argument("--generations", type=int, default=5, help="Number of generations")
    parser.add_argument("--layers", nargs='+', default=['L1', 'L2'], choices=['L1', 'L2'], help="Optimization layers to use (L1=Intent, L2=Syntax)")
    parser.add_argument("--visualize", action='store_true', help="Generate comprehensive visualizations after optimization")
    args = parser.parse_args()

    # Initialize Logger
    experiment_logger = ExperimentLogger()
    experiment_logger.log_config(vars(args))

    # Read target code
    with open(args.target, "r") as f:
        initial_code = f.read()
    
    # Read test code
    with open(args.tests, "r") as f:
        test_code = f.read()

    # Initialize components
    logger.info("Initializing HEDGE components...")
    
    # 1. Green Gym
    runner = CodeRunner(timeout_seconds=20)
    
    # 2. Abstraction Layer & LLM
    llm_client = get_llm_client()
    abstraction_manager = AbstractionManager(llm_client)
    
    # 3. Mutators
    mutators = []
    
    # L2 Mutators (Formal + Simple + Neural L2)
    if 'L2' in args.layers:
        logger.info("Enabling L2 Mutators (Syntax/AST + Neural Refactoring)")
        mutators.append(FormalMutator())
        mutators.append(SimpleMutator())
        
    # LLM Mutator (Configured based on layers)
    enable_l1 = 'L1' in args.layers
    enable_l2 = 'L2' in args.layers
    
    if enable_l1:
        logger.info("Enabling L1 Mutators (Intent/Algorithmic)")
        
    if enable_l1 or enable_l2:
        llm_mutator = LLMMutator(llm_client, abstraction_manager, enable_l1=enable_l1, enable_l2=enable_l2)
        mutators.append(llm_mutator)
    
    # 4. Engine
    engine = EvolutionaryEngine(mutators, runner, experiment_logger=experiment_logger, generations=args.generations)
    
    # Run optimization
    logger.info(f"Starting optimization loop with layers: {args.layers}")
    pareto_solutions = engine.optimize(initial_code, test_code)
    
    print("\n" + "="*50)
    print("OPTIMIZATION COMPLETE")
    print("="*50)
    print(f"Found {len(pareto_solutions)} Pareto-optimal solutions.")
    
    results = []
    for i, sol in enumerate(pareto_solutions):
        print(f"\nSolution {i+1} [{sol.mutation_type}]:")
        print(f"  Metrics: {sol.metrics}")
        print(f"  Code Length: {len(sol.code)} chars")
        results.append({
            "id": sol.variant_id,
            "metrics": sol.metrics,
            "mutation": sol.mutation_type,
            "code": sol.code
        })

    # Save Pareto results
    output_path = experiment_logger.save_artifact("pareto_results.json", json.dumps(results, indent=2))
    logger.info(f"Pareto results saved to {output_path}")
    
    # Save best solution (by energy) to original location for convenience
    if pareto_solutions:
        # Sort by energy
        best_sol = sorted(pareto_solutions, key=lambda s: s.metrics.get("energy_joules", float('inf')))[0]
        local_output = args.target.replace(".py", "_optimized.py")
        with open(local_output, "w") as f:
            f.write(best_sol.code)
        print(f"\nBest Energy Solution saved to {local_output}")
    
    # Generate visualizations if requested
    if args.visualize:
        print("\n" + "="*50)
        visualizer = ExperimentVisualizer(experiment_logger.experiment_dir)
        visualizer.generate_all_visualizations()
        print("="*50)

if __name__ == "__main__":
    main()
