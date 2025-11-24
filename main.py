import argparse
import logging
import sys
import os

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
from src.mutator.llm_mutator import LLMMutator
from src.core.llm import get_llm_client
from src.core.abstraction import AbstractionManager
from src.core.engine import EvolutionaryEngine

from src.utils.logging import ExperimentLogger

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="HEDGE: Hierarchical Evolutionary Darwin-Green Engine")
    parser.add_argument("--target", type=str, required=True, help="Path to the target python file to optimize")
    parser.add_argument("--tests", type=str, required=True, help="Path to the test file")
    parser.add_argument("--generations", type=int, default=5, help="Number of generations")
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
    # We use:
    # - SimpleMutator (Generic AST transformations)
    # - RobustMutator (Additional AST optimizations)
    # - LLMMutator (L1/Intent & L2/Direct)
    simple_mutator = SimpleMutator()
    robust_mutator = RobustMutator()
    llm_mutator = LLMMutator(llm_client, abstraction_manager)
    
    mutators = [simple_mutator, robust_mutator, llm_mutator]
    
    # 4. Engine
    engine = EvolutionaryEngine(mutators, runner, experiment_logger=experiment_logger, generations=args.generations)
    
    # Run optimization
    logger.info("Starting optimization loop...")
    best_code, best_metrics = engine.optimize(initial_code, test_code)
    
    print("\n" + "="*50)
    print("OPTIMIZATION COMPLETE")
    print("="*50)
    print(f"Best Metrics: {best_metrics}")
    print("-" * 20)
    print("Best Code:")
    print(best_code)
    print("="*50)

    # Save best code
    output_path = experiment_logger.save_artifact("best_optimized.py", best_code)
    logger.info(f"Optimized code saved to {output_path}")
    
    # Also save to original location for convenience
    local_output = args.target.replace(".py", "_optimized.py")
    with open(local_output, "w") as f:
        f.write(best_code)

if __name__ == "__main__":
    main()
