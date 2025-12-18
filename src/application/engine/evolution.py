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
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from pathlib import Path

from src.domain.interfaces import Mutator, CodeRunner
from src.domain.ir.schema import Module
from src.domain.ir.validators import IRValidator
from src.domain.ir.metrics import IRMetricsCollector, MutationStatistics
from src.domain.ir.serialization import IRSerializer, IRDiffer
from src.infrastructure.parsing.python_parser import PythonParser
from src.infrastructure.codegen.python_codegen import PythonCodeGenerator
from src.application.engine.crossover import CrossoverManager
from src.application.mutators.base import MutationOrchestrator, MutationLayer

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
    """Maintains a set of non-dominated solutions with diversity preservation."""
    
    def __init__(self, max_size: int = 50):
        self.solutions: List[Solution] = []
        self.max_size = max_size
    
    def _dominates(self, sol_a: Solution, sol_b: Solution) -> bool:
        """Check if sol_a dominates sol_b in the Pareto sense."""
        a_energy = sol_a.metrics.get("energy_joules", float('inf'))
        a_time = sol_a.metrics.get("duration_seconds", float('inf'))
        
        b_energy = sol_b.metrics.get("energy_joules", float('inf'))
        b_time = sol_b.metrics.get("duration_seconds", float('inf'))
        
        better_in_one = (a_energy < b_energy) or (a_time < b_time)
        no_worse = (a_energy <= b_energy) and (a_time <= b_time)
        
        return better_in_one and no_worse
    
    def _crowding_distance(self, solutions: List[Solution]) -> Dict[str, float]:
        """Calculate crowding distance for diversity preservation."""
        if len(solutions) <= 2:
            return {sol.variant_id: float('inf') for sol in solutions}
        
        distances = {sol.variant_id: 0.0 for sol in solutions}
        
        # Sort by each objective and calculate distances
        objectives = ["energy_joules", "duration_seconds"]
        
        for obj in objectives:
            # Sort solutions by this objective
            sorted_sols = sorted(solutions, key=lambda s: s.metrics.get(obj, float('inf')))
            
            # Boundary solutions get infinite distance
            if len(sorted_sols) > 0:
                distances[sorted_sols[0].variant_id] = float('inf')
                distances[sorted_sols[-1].variant_id] = float('inf')
            
            # Calculate range for normalization
            obj_min = sorted_sols[0].metrics.get(obj, 0)
            obj_max = sorted_sols[-1].metrics.get(obj, 1)
            obj_range = obj_max - obj_min
            
            if obj_range > 0:
                # Calculate distances for intermediate solutions
                for i in range(1, len(sorted_sols) - 1):
                    if distances[sorted_sols[i].variant_id] != float('inf'):
                        prev_val = sorted_sols[i-1].metrics.get(obj, 0)
                        next_val = sorted_sols[i+1].metrics.get(obj, 0)
                        distances[sorted_sols[i].variant_id] += (next_val - prev_val) / obj_range
        
        return distances
    
    def update(self, new_solution: Solution) -> bool:
        """Add solution if it's non-dominated, with diversity preservation."""
        # Check if any existing solution dominates the new one
        for sol in self.solutions:
            if self._dominates(sol, new_solution):
                return False
        
        # Remove solutions dominated by the new one
        self.solutions = [s for s in self.solutions if not self._dominates(new_solution, s)]
        
        self.solutions.append(new_solution)
        
        # Apply diversity preservation if archive is too large
        if len(self.solutions) > self.max_size:
            self._maintain_diversity()
        
        return True
    
    def _maintain_diversity(self):
        """Maintain diversity by removing crowded solutions."""
        if len(self.solutions) <= self.max_size:
            return
        
        # Calculate crowding distances
        distances = self._crowding_distance(self.solutions)
        
        # Sort by crowding distance (ascending) and remove most crowded
        sorted_solutions = sorted(self.solutions, key=lambda s: distances[s.variant_id])
        
        # Keep the least crowded solutions
        num_to_remove = len(self.solutions) - self.max_size
        self.solutions = sorted_solutions[num_to_remove:]

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
        self.crossover_manager = CrossoverManager()
        self.mutation_orchestrator = MutationOrchestrator()
        
        # Register mutators with orchestrator
        self._register_layered_mutators()
        
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
    
    def optimize(self, initial_code: str, test_code: str, progress_callback=None) -> List[Solution]:
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
        
        Args:
            initial_code: Source code to optimize
            test_code: Test harness code
            progress_callback: Optional callable(candidates_count: int) to report progress
            
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
        import random
        import math

        for gen in range(1, self.generations + 1):
            logger.info(f"Generation {gen}/{self.generations}...")
            next_gen_candidates = []
            
            # Get parents from archive
            parents = self.archive.solutions
            if not parents:
                break
            
            # --- Probabilistic Selection ---
            # Calculate fitness scores
            # Fitness = 1 / (Energy * Time) (Simplified)
            # We want to minimize Energy and Time, so maximize Fitness.
            
            fitness_scores = []
            for p in parents:
                energy = p.metrics.get("energy_joules", 1e-6)
                duration = p.metrics.get("duration_seconds", 1e-6)
                # Avoid division by zero
                if energy <= 0: energy = 1e-9
                if duration <= 0: duration = 1e-9
                
                # We can weigh energy more if desired, but let's keep it balanced for now
                score = 1.0 / (energy * duration)
                fitness_scores.append(score)
            
            # Normalize scores to probabilities (Softmax-like or simple proportion)
            # Using simple proportion for now, but softmax handles outliers better?
            # Let's use Softmax to ensure "slightly worse" gets "slightly less" chance.
            
            # Shift for numerical stability
            max_score = max(fitness_scores)
            exp_scores = [math.exp((s - max_score)) for s in fitness_scores] # This might be too aggressive if scores vary widely
            
            # Let's use a simpler proportional approach but with a baseline
            # Or just use the raw fitness if they are close.
            # The user asked for: "relative performance is reflected in their chances"
            
            total_fitness = sum(fitness_scores)
            probs = [s / total_fitness for s in fitness_scores]
            
            # Select parents based on probabilities
            # We want to generate roughly same number of variants as before?
            # Or just pick N parents?
            # Let's pick parents for each mutation slot.
            
            # For each parent (selected probabilistically), apply mutators
            # We'll try to generate roughly len(parents) * len(mutators) variants
            
            num_selections = len(parents)
            selected_indices = random.choices(range(len(parents)), weights=probs, k=num_selections)
            selected_parents = [parents[i] for i in selected_indices]
            
            # Add diversity: also include some random parents that might have low fitness but are unique?
            # For now, the probabilistic selection handles "slightly worse" ones.
            
            # Generate variants through mutation
            for parent in selected_parents:
                # Adaptive selection of mutators
                active_mutators = self._select_mutators()
                
                for mutator in active_mutators:
                    try:
                        variants = mutator.mutate(parent.ir)
                        
                        for variant_ir, strategy_name in variants:
                            self.statistics.record_attempt(strategy_name)
                            
                            # Validate variant
                            val_result = self.validator.validate(variant_ir)
                            if val_result.valid:
                                self.statistics.record_success(strategy_name)
                                next_gen_candidates.append((variant_ir, parent, strategy_name))
                            else:
                                logger.warning(f"Variant rejected: {val_result.errors}")
                                self.statistics.failed_validations += 1
                    except Exception as e:
                        logger.error(f"Mutator {mutator.__class__.__name__} failed: {e}")
            
            # Generate variants through crossover (if we have multiple parents)
            if len(selected_parents) >= 2:
                num_crossovers = min(len(selected_parents) // 2, 3)  # Limit crossover attempts
                
                for _ in range(num_crossovers):
                    parent1, parent2 = random.sample(selected_parents, 2)
                    
                    try:
                        offspring = self.crossover_manager.perform_crossover(parent1.ir, parent2.ir)
                        
                        for child_ir in offspring:
                            self.statistics.record_attempt("Crossover")
                            
                            # Validate offspring
                            val_result = self.validator.validate(child_ir)
                            if val_result.valid:
                                self.statistics.record_success("Crossover")
                                # Use parent1 as the "parent" for tracking
                                next_gen_candidates.append((child_ir, parent1, "Crossover"))
                            else:
                                logger.warning(f"Crossover offspring rejected: {val_result.errors}")
                                self.statistics.failed_validations += 1
                    except Exception as e:
                        logger.error(f"Crossover failed: {e}")
            
            if not next_gen_candidates:
                logger.info("No valid variants produced. Stopping.")
                break
            
            # Evaluate variants
            candidates_evaluated = 0
            for variant_ir, parent, mutator_name in next_gen_candidates:
                variant_id = str(uuid.uuid4())
                
                success, metrics, output = self._evaluate(variant_ir, test_code)
                candidates_evaluated += 1
                
                if progress_callback:
                    # Report total progress across usage? Or just update call
                    # Let's pass the iteration count or something useful
                    progress_callback(1) 
                
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
                        self.statistics.record_improvement(mutator_name)
                        logger.info(f"New Pareto solution! [{mutator_name}] {metrics}")
            
            logger.info(f"Generation {gen} complete. Archive size: {len(self.archive.solutions)}")
            logger.debug(f"Process stats: {self.statistics.to_dict()}")
        
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

    def _select_mutators(self) -> List[Mutator]:
        """
        Select mutators to apply based on past performance.
        Uses an adaptive schedule where mutators with higher improvement
        rates have a higher probability of being selected.
        """
        import random
        
        if not self.statistics.mutator_stats:
            # No data yet, return all
            return self.mutators
            
        scores = {}
        for m in self.mutators:
            # Aggregate stats by matching prefix
            # e.g. StructuralMutator -> "Structural"
            name_prefix = m.__class__.__name__.replace("Mutator", "")
            if name_prefix == "Structural": 
                # Structural produces "Structural_XXX"
                pass
            
            total_improved = 0
            total_attempts = 0
            
            for strat, data in self.statistics.mutator_stats.items():
                if strat.startswith(name_prefix):
                    total_improved += data["improved"]
                    total_attempts += data["total"]
            
            rate = 0.0
            if total_attempts > 0:
                rate = total_improved / total_attempts
            
            # Base score + rate (ensure non-zero)
            scores[m] = rate + 0.01

        if not scores:
            return self.mutators

        # Calculate acceptance probability
        # Normalize relative to best performer
        max_score = max(scores.values())
        
        selected = []
        for m in self.mutators:
            score = scores[m]
            # Prob formula: Min 20% + 80% * relative_performance
            prob = 0.2 + 0.8 * (score / max_score)
            
            if random.random() < prob:
                selected.append(m)
        
        # Ensure at least one mutator is selected
        if not selected:
            selected = [random.choice(self.mutators)]
            
        return selected
    
    def _register_layered_mutators(self):
        """Register layered mutators with the orchestrator."""
        # This will be called from the CLI setup to register the appropriate mutators
        # based on the selected optimization level and enabled layers
        pass
    
    def set_enabled_layers(self, enabled_layers: Set[MutationLayer]):
        """Set which mutation layers are enabled for this optimization run."""
        self.enabled_layers = enabled_layers
    
    def apply_layered_mutations(self, ir: Module) -> List[Tuple[Module, str]]:
        """Apply mutations using the layered orchestrator."""
        if hasattr(self, 'enabled_layers'):
            return self.mutation_orchestrator.apply_layered_mutations(ir, self.enabled_layers)
        else:
            return self.mutation_orchestrator.apply_layered_mutations(ir)
