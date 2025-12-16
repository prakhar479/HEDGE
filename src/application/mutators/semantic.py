import json
import logging
from typing import List, Tuple, Optional
from src.domain.interfaces import Mutator
from src.domain.ir import schema
from src.infrastructure.parsing.python_parser import PythonParser
from src.infrastructure.codegen.python_codegen import PythonCodeGenerator

logger = logging.getLogger(__name__)


from src.application.mutators.semantic_base import LLMMutatorBase, logger

class SemanticMutator(LLMMutatorBase):
    """
    Uses LLM to perform high-level semantic optimizations (StdLib & Algorithmic).
    Strictly forbids external libraries.
    """
    
    def mutate(self, ir: schema.Module) -> List[Tuple[schema.Module, str]]:
        variants = []
        
        # Analyze existing imports
        allowed_imports = self._get_imports(ir)
        
        # Generate code from IR
        code = self.codegen.generate(ir)
        
        # Strategy 1: Library optimization (StdLib)
        variant = self._mutate_library(code, allowed_imports)
        if variant:
            variants.append((variant, "Semantic_Library"))
        
        # Strategy 2: Algorithmic improvement
        variant = self._mutate_algorithmic(code, allowed_imports)
        if variant:
            variants.append((variant, "Semantic_Algorithmic"))
        
        return variants

    def _validate_imports(self, new_ir: schema.Module, allowed_imports: set) -> bool:
        """Ensure no new unauthorized imports are added."""
        new_imports = self._get_imports(new_ir)
        
        STDLIB_WHITELIST = {
            'math', 'itertools', 'functools', 'collections', 'heapq', 'bisect',
            'typing', 'random', 'time', 'datetime', 're', 'sys', 'os', 'copy',
            'statistics', 'operator', 'string'
        }
        
        for imp in new_imports:
            if imp not in allowed_imports and imp not in STDLIB_WHITELIST:
                logger.warning(f"Semantic mutation rejected using unauthorized import: {imp}")
                return False
        return True

    def _mutate_with_prompt(self, code: str, system_prompt: str, allowed_imports: set) -> Optional[schema.Module]:
        """Generic mutation helper with CoT and repair."""
        try:
            # Enforce constraints in prompt
            constraint = "\nCONSTRAINT: Do NOT import any external libraries (numpy, pandas, etc) unless they are already imported. You may use standard library."
            full_prompt = system_prompt + constraint
            
            response = self.llm.complete(full_prompt).strip()
            optimized_code = self._clean_code(response)
            
            if optimized_code and optimized_code != code:
                new_ir = self._safe_parse(optimized_code)
                if new_ir:
                    if self._validate_imports(new_ir, allowed_imports):
                        return new_ir
        except Exception as e:
            logger.error(f"Mutation failed: {e}")
        return None
    
    def _mutate_library(self, code: str, allowed_imports: set) -> Optional[schema.Module]:
        """Replace manual implementations with standard library."""
        prompt = f"""You are an expert Python performance engineer.
Optimize the following code by replacing manual implementations with standard library functions.
Think step-by-step:
1. Identify common algorithms implemented manually (sorting, searching, counting).
2. Replace with `itertools`, `collections`, `functools`, or `math` equivalents.
3. Ensure performance is improved.

Return ONLY the Python code, no markdown, no explanations.

Code:
{code}
"""
        return self._mutate_with_prompt(code, prompt, allowed_imports)
    
    def _mutate_algorithmic(self, code: str, allowed_imports: set) -> Optional[schema.Module]:
        """Improve algorithmic complexity."""
        prompt = f"""You are an expert algorithm designer.
Analyze the following code and optimize its time or space complexity.
Think step-by-step:
1. Analyze the current Big-O complexity.
2. Identify bottlenecks.
3. Propose a more efficient data structure or algorithm.
4. Implement the optimization.

Return ONLY the Python code, no markdown, no explanations.

Code:
{code}
"""
        return self._mutate_with_prompt(code, prompt, allowed_imports)

