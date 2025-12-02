from typing import List, Tuple
import logging
from .base import Mutator
from src.core.llm import LLMClient
from src.core.abstraction import AbstractionManager

logger = logging.getLogger(__name__)

class LLMMutator(Mutator):
    def __init__(self, llm_client: LLMClient, abstraction_manager: AbstractionManager, enable_l1: bool = True, enable_l2: bool = True):
        self.llm = llm_client
        self.abstraction = abstraction_manager
        self.enable_l1 = enable_l1
        self.enable_l2 = enable_l2

    def mutate(self, code_str: str) -> List[Tuple[str, str]]:
        """
        Generates variants using LLM-based mutations.
        Strategies:
        1. L1 Mutation: Lift -> Optimize Intent -> Lower.
        2. L2 Mutation: Direct code refactoring (Neural).
        """
        variants = []
        
        # Strategy 1: L1 Mutation (Hierarchical)
        if self.enable_l1:
            variants.extend(self._mutate_l1(code_str))

        # Strategy 2: L2 Neural Mutations
        if self.enable_l2:
            variants.extend(self._mutate_idioms(code_str))
            variants.extend(self._mutate_libraries(code_str))
            variants.extend(self._mutate_vectorization(code_str))
            
        return variants

    def _clean_code(self, code: str) -> str:
        if code.startswith("```python"):
            code = code.split("```python")[1]
        elif code.startswith("```"):
            code = code.split("```")[1]
        if code.endswith("```"):
            code = code.rsplit("```", 1)[0]
        return code.strip()

    def _mutate_l1(self, code_str: str) -> List[Tuple[str, str]]:
        variants = []
        try:
            intent = self.abstraction.lift(code_str)
            if intent:
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
                        variants.append((new_code, "LLM_L1_Intent"))
        except Exception as e:
            logger.error(f"L1 Mutation failed: {e}")
        return variants

    def _mutate_idioms(self, code_str: str) -> List[Tuple[str, str]]:
        variants = []
        try:
            prompt = f"""
You are an expert Python developer.
Refactor the following code to be more "Pythonic" and idiomatic.
Use list comprehensions, generator expressions, or built-in functions where appropriate.
Return ONLY the python code, no markdown, no explanations.

Code:
{code_str}

Idiomatic Code:
"""
            optimized_code = self.llm.complete(prompt).strip()
            optimized_code = self._clean_code(optimized_code)
            
            if optimized_code and optimized_code != code_str:
                variants.append((optimized_code, "LLM_L2_Idiom"))
        except Exception as e:
            logger.error(f"Idiomatic Mutation failed: {e}")
        return variants

    def _mutate_libraries(self, code_str: str) -> List[Tuple[str, str]]:
        variants = []
        try:
            prompt = f"""
You are an expert Python performance engineer.
Optimize the following code by replacing manual implementations with standard library functions (e.g., itertools, collections, math).
Return ONLY the python code, no markdown, no explanations.

Code:
{code_str}

Optimized Code:
"""
            optimized_code = self.llm.complete(prompt).strip()
            optimized_code = self._clean_code(optimized_code)
            
            if optimized_code and optimized_code != code_str:
                variants.append((optimized_code, "LLM_L2_Library"))
        except Exception as e:
            logger.error(f"Library Mutation failed: {e}")
        return variants

    def _mutate_vectorization(self, code_str: str) -> List[Tuple[str, str]]:
        variants = []
        try:
            prompt = f"""
You are an expert in Numerical Python.
If the following code involves loops over numbers, convert it to use NumPy vectorization for speed.
If NumPy is not applicable or wouldn't help, just return the original code.
Return ONLY the python code, no markdown, no explanations.

Code:
{code_str}

Vectorized Code:
"""
            optimized_code = self.llm.complete(prompt).strip()
            optimized_code = self._clean_code(optimized_code)
            
            if optimized_code and optimized_code != code_str:
                variants.append((optimized_code, "LLM_L2_Vectorization"))
        except Exception as e:
            logger.error(f"Vectorization Mutation failed: {e}")
        return variants
