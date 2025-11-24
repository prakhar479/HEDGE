from typing import List
import logging
from .base import Mutator
from src.core.llm import LLMClient
from src.core.abstraction import AbstractionManager

logger = logging.getLogger(__name__)

class LLMMutator(Mutator):
    def __init__(self, llm_client: LLMClient, abstraction_manager: AbstractionManager):
        self.llm = llm_client
        self.abstraction = abstraction_manager

    def mutate(self, code_str: str) -> List[str]:
        """
        Generates variants using LLM-based mutations.
        Strategies:
        1. L1 Mutation: Lift -> Optimize Intent -> Lower.
        2. L2 Mutation: Direct code refactoring (e.g., "Make this pythonic").
        """
        variants = []
        
        # Strategy 1: L1 Mutation (Hierarchical)
        try:
            intent = self.abstraction.lift(code_str)
            if intent:
                # Ask LLM to optimize the intent
                prompt = f"""
You are an expert algorithm designer.
Optimize the following algorithmic intent for better time complexity or energy efficiency.
Provide ONLY the optimized intent summary, no explanations.

Current Intent: {intent}

Optimized Intent:
"""
                optimized_intent = self.llm.complete(prompt).strip()
                if optimized_intent and optimized_intent != intent:
                    logger.info(f"Optimized Intent: {optimized_intent}")
                    new_code = self.abstraction.lower(optimized_intent)
                    if new_code:
                        variants.append(new_code)
        except Exception as e:
            logger.error(f"L1 Mutation failed: {e}")

        # Strategy 2: L2 Mutation (Direct Optimization)
        try:
            prompt = f"""
You are an expert Python performance engineer.
Optimize the following code for execution speed and energy efficiency.
Use efficient data structures, vectorization (if applicable), or better standard library functions.
Return ONLY the python code, no markdown, no explanations.

Code:
{code_str}

Optimized Code:
"""
            optimized_code = self.llm.complete(prompt).strip()
            
            # Cleanup code
            if optimized_code.startswith("```python"):
                optimized_code = optimized_code.split("```python")[1]
            if optimized_code.startswith("```"):
                optimized_code = optimized_code.split("```")[1]
            if optimized_code.endswith("```"):
                optimized_code = optimized_code.rsplit("```", 1)[0]
            
            optimized_code = optimized_code.strip()
            
            if optimized_code and optimized_code != code_str:
                variants.append(optimized_code)
                
        except Exception as e:
            logger.error(f"L2 Mutation failed: {e}")
            
        return variants
