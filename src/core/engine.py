import logging
import copy
import random
import uuid
import hashlib
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field
from src.green_gym.runner import CodeRunner
from src.mutator.base import Mutator
from src.utils.logging import ExperimentLogger

logger = logging.getLogger(__name__)

@dataclass
class Solution:
    code: str
    metrics: Dict[str, float]
    variant_id: str
    parent_id: str
    mutation_type: str
    generation: int

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        if not isinstance(other, Solution):
            return NotImplemented
        return self.code == other.code

class ParetoArchive:
    def __init__(self):
        self.solutions: List[Solution] = []

    def _dominates(self, sol_a: Solution, sol_b: Solution) -> bool:
        """
        Returns True if sol_a dominates sol_b.
        Objectives (minimize): energy_joules, duration_seconds
        """
        a_energy = sol_a.metrics.get("energy_joules", float('inf'))
        a_time = sol_a.metrics.get("duration_seconds", float('inf'))
        
        b_energy = sol_b.metrics.get("energy_joules", float('inf'))
        b_time = sol_b.metrics.get("duration_seconds", float('inf'))

        # If energy is 0 (measurement failed), treat as high cost unless time is significantly better?
        # For simplicity, we assume valid metrics.
        
        better_in_one = (a_energy < b_energy) or (a_time < b_time)
        no_worse = (a_energy <= b_energy) and (a_time <= b_time)
        
        return better_in_one and no_worse

    def update(self, new_solution: Solution) -> bool:
        """
        Attempts to add new_solution to the archive.
        Returns True if added, False if dominated.
        """
        # Check if dominated by any existing solution
        for sol in self.solutions:
            if self._dominates(sol, new_solution):
                return False
            
            # Check if identical code already exists (deduplication)
            if sol.code == new_solution.code:
                # Keep the one with better metrics (though they should be similar)
                if self._dominates(new_solution, sol):
                    self.solutions.remove(sol)
                    self.solutions.append(new_solution)
                    return True
                return False

        # Remove solutions dominated by the new one
        self.solutions = [s for s in self.solutions if not self._dominates(new_solution, s)]
        
        self.solutions.append(new_solution)
        return True

class EvolutionaryEngine:
    def __init__(self, 
                 mutators: List[Mutator], 
                 runner: CodeRunner, 
                 experiment_logger: Optional[ExperimentLogger] = None,
                 generations: int = 10, 
                 population_size: int = 5):
        self.mutators = mutators
        self.runner = runner
        self.logger = experiment_logger
        self.generations = generations
        self.population_size = population_size
        self.archive = ParetoArchive()
        self.cache: Dict[str, Dict[str, float]] = {} # Cache code hash -> metrics

    def _evaluate(self, code: str, test_code: str) -> Tuple[bool, Dict[str, float], str]:
        # Check cache
        code_hash = hashlib.md5(code.encode()).hexdigest()
        if code_hash in self.cache:
            return True, self.cache[code_hash], "Cached"

        success, metrics, output = self.runner.run(code, test_code)
        
        if success:
            self.cache[code_hash] = metrics
            
        return success, metrics, output

    def optimize(self, initial_code: str, test_code: str) -> List[Solution]:
        """
        Runs the hierarchical evolutionary loop with Pareto optimization.
        """
        root_id = str(uuid.uuid4())
        
        # 1. Baseline
        logger.info("Running baseline...")
        success, metrics, output = self._evaluate(initial_code, test_code)
        
        if self.logger:
            self.logger.log_evaluation(
                generation=0,
                variant_id=root_id,
                parent_id="ROOT",
                mutation_type="BASELINE",
                code=initial_code,
                metrics=metrics,
                success=success
            )

        if not success:
            logger.error(f"Baseline failed: {output}")
            return []
        
        baseline_solution = Solution(
            code=initial_code,
            metrics=metrics,
            variant_id=root_id,
            parent_id="ROOT",
            mutation_type="BASELINE",
            generation=0
        )
        self.archive.update(baseline_solution)
        
        logger.info(f"Baseline metrics: {metrics}")

        # Population for next generation (starts with baseline)
        population = [baseline_solution]

        for gen in range(1, self.generations + 1):
            logger.info(f"Generation {gen}...")
            next_gen_candidates = []
            
            # Select parents from archive + current population (elitism + diversity)
            # For now, just use the archive as the pool
            parents = self.archive.solutions
            
            if not parents:
                break

            # Generate variants
            for parent in parents:
                for mutator in self.mutators:
                    try:
                        mut_variants = mutator.mutate(parent.code)
                        # mut_variants is List[Tuple[str, str]] -> (code, strategy_name)
                        for v_code, strategy_name in mut_variants:
                            next_gen_candidates.append((v_code, parent, strategy_name))
                    except Exception as e:
                        logger.error(f"Mutator failed: {e}")
            
            if not next_gen_candidates:
                logger.info("No variants produced. Stopping.")
                break
                
            # Evaluate candidates
            for i, (variant_code, parent, mutator_name) in enumerate(next_gen_candidates):
                variant_id = str(uuid.uuid4())
                success, metrics, output = self._evaluate(variant_code, test_code)
                
                if self.logger:
                    self.logger.log_evaluation(
                        generation=gen,
                        variant_id=variant_id,
                        parent_id=parent.variant_id,
                        mutation_type=mutator_name,
                        code=variant_code,
                        metrics=metrics,
                        success=success
                    )
                
                if success:
                    new_sol = Solution(
                        code=variant_code,
                        metrics=metrics,
                        variant_id=variant_id,
                        parent_id=parent.variant_id,
                        mutation_type=mutator_name,
                        generation=gen
                    )
                    added = self.archive.update(new_sol)
                    if added:
                        logger.info(f"New Pareto optimal solution found! [{mutator_name}] {metrics}")
            
            # Log generation summary
            logger.info(f"Generation {gen} complete. Archive size: {len(self.archive.solutions)}")
            
        return self.archive.solutions
