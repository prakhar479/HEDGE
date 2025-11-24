import logging
import copy
import random
import uuid
from typing import List, Tuple, Dict, Any, Optional
from src.green_gym.runner import CodeRunner
from src.mutator.base import Mutator
from src.utils.logging import ExperimentLogger

logger = logging.getLogger(__name__)

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
        self.history = []

    def optimize(self, initial_code: str, test_code: str) -> Tuple[str, Dict[str, Any]]:
        """
        Runs the hierarchical evolutionary loop.
        """
        current_best_code = initial_code
        current_best_id = str(uuid.uuid4())
        
        # 1. Baseline
        logger.info("Running baseline...")
        success, metrics, output = self.runner.run(current_best_code, test_code)
        
        if self.logger:
            self.logger.log_evaluation(
                generation=0,
                variant_id=current_best_id,
                parent_id="ROOT",
                mutation_type="BASELINE",
                code=current_best_code,
                metrics=metrics,
                success=success
            )

        if not success:
            logger.error(f"Baseline failed: {output}")
            return initial_code, {"error": "Baseline failed"}
        
        current_best_metrics = metrics
        self.history.append({
            "generation": 0,
            "code": current_best_code,
            "metrics": current_best_metrics,
            "output": output
        })
        
        logger.info(f"Baseline metrics: {current_best_metrics}")

        for gen in range(1, self.generations + 1):
            logger.info(f"Generation {gen}...")
            
            # Generate variants using all available mutators (L1 and L2)
            variants = []
            
            # We need to track which mutator produced which variant
            # Structure: (code, mutator_name)
            
            for mutator in self.mutators:
                try:
                    mut_variants = mutator.mutate(current_best_code)
                    mutator_name = mutator.__class__.__name__
                    for v in mut_variants:
                        variants.append((v, mutator_name))
                except Exception as e:
                    logger.error(f"Mutator failed: {e}")
            
            # If no variants produced, stop
            if not variants:
                logger.info("No variants produced. Stopping.")
                break
                
            # Evaluate variants
            found_better = False
            
            for i, (variant_code, mutator_name) in enumerate(variants):
                variant_id = str(uuid.uuid4())
                success, metrics, output = self.runner.run(variant_code, test_code)
                
                if self.logger:
                    self.logger.log_evaluation(
                        generation=gen,
                        variant_id=variant_id,
                        parent_id=current_best_id,
                        mutation_type=mutator_name,
                        code=variant_code,
                        metrics=metrics,
                        success=success
                    )
                
                if success:
                    # Selection Logic: Simple improvement check
                    is_better = False
                    
                    # Prioritize Energy if available and non-zero
                    current_energy = current_best_metrics.get("energy_joules", 0)
                    new_energy = metrics.get("energy_joules", 0)
                    
                    if current_energy > 0 and new_energy > 0:
                        if new_energy < current_energy:
                            is_better = True
                    else:
                        # Fallback to time
                        if metrics.get("duration_seconds", float('inf')) < current_best_metrics.get("duration_seconds", float('inf')):
                            is_better = True
                            
                    if is_better:
                        # Determine Layer based on mutator name
                        layer = "L1 (Intent)" if "LLM" in mutator_name else "L2 (Syntax)"
                        logger.info(f"Found better variant! [{layer} - {mutator_name}] {metrics}")
                        current_best_code = variant_code
                        current_best_metrics = metrics
                        current_best_id = variant_id # Update parent ID for next generation
                        found_better = True
            
            # Log generation best
            self.history.append({
                "generation": gen,
                "code": current_best_code,
                "metrics": current_best_metrics
            })
            
        return current_best_code, current_best_metrics
