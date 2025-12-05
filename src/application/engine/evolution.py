"""
Evolutionary Engine - IR-Only Optimization System

This is the core orchestration layer that coordinates:
- IR parsing and validation
- Mutation generation
- Code reconstruction
- Evaluation and Pareto optimization

Key principles:
1. IR is the single source of truth
2. All mutations are validated before evaluation
3. Code is reconstructed from IR (never cached)
4. Comprehensive metrics and instrumentation
"""
import logging
import uuid
import hashlib
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

from src.domain.interfaces import Mutator, CodeRunner
from src.domain.ir.schema import Module
from src.domain.ir.validators import IRValidator
from src.domain.ir.metrics import IRMetricsCollector, MutationStatistics
from src.domain.ir.serialization import IRSerializer, IRDiffer
from src.infrastructure.parsing.python_parser import PythonParser
from src.infrastructure.codegen.python_codegen import PythonCodeGenerator

logger = logging.getLogger(__name__)

@dataclass
class Solution:
    """Represents a candidate solution in the evolutionary search."""
    ir: Module
    metrics: Dict[str, float]
    variant_id: str
    parent_id: str
    mutation_type: str
    generation: int

class ParetoArchive:
    """Maintains a set of non-dominated solutions."""
    
    def __init__(self):
        self.solutions: List[Solution] = []
    
    def _dominates(self, sol_a: Solution, sol_b: Solution) -> bool:
        """Check if sol_a dominates sol_b in the Pareto sense."""
        a_energy = sol_a.metrics.get("energy_joules", float('inf'))
        a_time = sol_a.metrics.get("duration_seconds", float('inf'))
        
        b_energy = sol_b.metrics.get("energy_joules", float('inf'))
        b_time = sol_b.metrics.get("duration_seconds", float('inf'))
        
        better_in_one = (a_energy < b_energy) or (a_time < b_time)
        no_worse = (a_energy <= b_energy) and (a_time <= b_time)
        
        return better_in_one and no_worse
    
    def update(self, new_solution: Solution) -> bool:
        """Add solution if it's non-dominated."""
        # Check if any existing solution dominates the new one
        for sol in self.solutions:
            if self._dominates(sol, new_solution):
                return False
        
        # Remove solutions dominated by the new one
        self.solutions = [s for s in self.solutions if not self._dominates(new_solution, s)]
        
        self.solutions.append(new_solution)
        return True

class EvolutionaryEngine:
    """
    Main evolutionary optimization engine.
    
    Enforces IR-Only mutations with strict validation.
    Provides comprehensive instrumentation and metrics.
    """
    
    def __init__(
        self,
        mutators: List[Mutator],
        runner: CodeRunner,
        generations: int = 10,
        population_size: int = 5,
        experiment_dir: Optional[Path] = None,
        save_ir_snapshots: bool = False
    ):
        """
        Initialize the evolutionary engine.
        
        Args:
            mutators: List of mutation strategies to apply
            runner: Code execution environment
            generations: Number of evolutionary generations
            population_size: Target population size (not currently used)
            experiment_dir: Directory to save experiment artifacts
            save_ir_snapshots: If True, save IR at each generation
        """
        self.mutators = mutators
        self.runner = runner
        self.generations = generations
        self.population_size = population_size
        self.experiment_dir = experiment_dir
        self.save_ir_snapshots = save_ir_snapshots
        
        # Core components
        self.parser = PythonParser()
        self.codegen = PythonCodeGenerator()
        self.validator = IRValidator()
        self.metrics_collector = IRMetricsCollector()
        
        # State
        self.archive = ParetoArchive()
        self.cache: Dict[str, Dict[str, float]] = {}
        self.statistics = MutationStatistics()
        
        # Setup experiment directory
        if self.experiment_dir:
            self.experiment_dir.mkdir(parents=True, exist_ok=True)
            if self.save_ir_snapshots:
                (self.experiment_dir / "ir_snapshots").mkdir(exist_ok=True)
    
    def _evaluate(self, ir: Module, test_code: str) -> Tuple[bool, Dict[str, float], str]:
        """
        Evaluate a solution by:
        1. Reconstructing code from IR
        2. Running it through the test harness
        3. Caching results
        """
        # Reconstruct code from IR
        code = self.codegen.generate(ir)
        
        # Check cache
        code_hash = hashlib.md5(code.encode()).hexdigest()
        if code_hash in self.cache:
            return True, self.cache[code_hash], "Cached"
        
        # Run the code
        success, metrics, output = self.runner.run(code, test_code)
        
        if success:
            self.cache[code_hash] = metrics
        
        return success, metrics, output
    
    def optimize(self, initial_code: str, test_code: str) -> List[Solution]:
        """
        Main optimization loop.
        
        Pipeline:
        1. Parse initial code → IR
        2. Validate IR
        3. For each generation:
            a. Mutate IR → new IR
            b. Validate new IR
            c. Reconstruct code from new IR
            d. Evaluate code
            e. Update Pareto archive
        
        Returns:
            List of Pareto-optimal solutions, or empty list if baseline fails
        """
        root_id = str(uuid.uuid4())
        
        # Parse baseline with error handling
        logger.info("Parsing baseline code...")
        try:
            baseline_ir = self.parser.parse(initial_code)
        except SyntaxError as e:
            logger.error(f"Failed to parse baseline code: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error parsing baseline: {e}")
            return []
        
        # Validate baseline
        val_result = self.validator.validate(baseline_ir)
        if not val_result.valid:
            logger.error(f"Baseline IR validation failed: {val_result.errors}")
            return []
        
        # Evaluate baseline
        logger.info("Evaluating baseline...")
        try:
            success, metrics, output = self._evaluate(baseline_ir, test_code)
        except Exception as e:
            logger.error(f"Failed to evaluate baseline: {e}")
            return []
        
        if not success:
            logger.error(f"Baseline execution failed: {output}")
            return []
        
        baseline_solution = Solution(
            ir=baseline_ir,
            metrics=metrics,
            variant_id=root_id,
            parent_id="ROOT",
            mutation_type="BASELINE",
            generation=0
        )
        self.archive.update(baseline_solution)
        
        # Save baseline IR
        self._save_ir_snapshot(baseline_solution)
        
        logger.info(f"Baseline metrics: {metrics}")
        
        # Evolutionary loop
        for gen in range(1, self.generations + 1):
            logger.info(f"Generation {gen}/{self.generations}...")
            next_gen_candidates = []
            
            # Get parents from archive
            parents = self.archive.solutions
            if not parents:
                break
            
            # Generate variants
            for parent in parents:
                for mutator in self.mutators:
                    try:
                        variants = mutator.mutate(parent.ir)
                        
                        for variant_ir, strategy_name in variants:
                            # Validate variant
                            val_result = self.validator.validate(variant_ir)
                            if val_result.valid:
                                next_gen_candidates.append((variant_ir, parent, strategy_name))
                            else:
                                logger.warning(f"Variant rejected: {val_result.errors}")
                    except Exception as e:
                        logger.error(f"Mutator {mutator.__class__.__name__} failed: {e}")
            
            if not next_gen_candidates:
                logger.info("No valid variants produced. Stopping.")
                break
            
            # Evaluate variants
            for variant_ir, parent, mutator_name in next_gen_candidates:
                variant_id = str(uuid.uuid4())
                
                success, metrics, output = self._evaluate(variant_ir, test_code)
                
                if success:
                    new_sol = Solution(
                        ir=variant_ir,
                        metrics=metrics,
                        variant_id=variant_id,
                        parent_id=parent.variant_id,
                        mutation_type=mutator_name,
                        generation=gen
                    )
                    
                    # Save variant IR
                    self._save_ir_snapshot(new_sol)
                    
                    added = self.archive.update(new_sol)
                    if added:
                        logger.info(f"New Pareto solution! [{mutator_name}] {metrics}")
            
            logger.info(f"Generation {gen} complete. Archive size: {len(self.archive.solutions)}")
        
        return self.archive.solutions

    def _save_ir_snapshot(self, solution: Solution):
        """Save IR snapshot for a solution."""
        if not self.save_ir_snapshots or not self.experiment_dir:
            return
            
        filename = f"gen_{solution.generation:03d}_{solution.variant_id[:8]}.json"
        filepath = self.experiment_dir / "ir_snapshots" / filename
        
        try:
            IRSerializer.save(solution.ir, filepath)
        except Exception as e:
            logger.error(f"Failed to save IR snapshot: {e}")
