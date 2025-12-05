import json
import logging
from typing import List, Tuple, Optional
from src.domain.interfaces import Mutator
from src.domain.ir import schema
from src.infrastructure.parsing.python_parser import PythonParser
from src.infrastructure.codegen.python_codegen import PythonCodeGenerator

logger = logging.getLogger(__name__)

class SemanticMutator(Mutator):
    """
    Uses LLM to perform high-level semantic optimizations.
    Strategy: Code -> LLM -> Code -> Parse to IR -> Validate.
    Includes a self-repair loop for invalid generated code.
    """
    
    def __init__(self, llm_client, max_retries: int = 3):
        self.llm = llm_client
        self.parser = PythonParser()
        self.codegen = PythonCodeGenerator()
        self.max_retries = max_retries
    
    def mutate(self, ir: schema.Module) -> List[Tuple[schema.Module, str]]:
        variants = []
        
        # Generate code from IR
        code = self.codegen.generate(ir)
        
        # Strategy 1: Idiomatic refactoring
        variant = self._mutate_idiomatic(code)
        if variant:
            variants.append((variant, "Semantic_Idiomatic"))
        
        # Strategy 2: Library optimization
        variant = self._mutate_library(code)
        if variant:
            variants.append((variant, "Semantic_Library"))
        
        # Strategy 3: Algorithmic improvement
        variant = self._mutate_algorithmic(code)
        if variant:
            variants.append((variant, "Semantic_Algorithmic"))
        
        return variants
    
    def _clean_code(self, response: str) -> str:
        """Extract code from LLM response."""
        if "```python" in response:
            response = response.split("```python", 1)[1]
        elif "```" in response:
            response = response.split("```", 1)[1]
        
        if "```" in response:
            response = response.split("```", 1)[0]
            
        return response.strip()
    
    def _repair_code(self, broken_code: str, error_msg: str) -> Optional[schema.Module]:
        """Attempt to repair broken code using the LLM."""
        logger.info(f"Attempting to repair code. Error: {error_msg}")
        
        prompt = f"""You are an expert Python debugger.
The following code has a syntax error or is invalid.
Error: {error_msg}

Code:
{broken_code}

Fix the code and return ONLY the corrected Python code.
"""
        try:
            response = self.llm.complete(prompt).strip()
            fixed_code = self._clean_code(response)
            return self.parser.parse(fixed_code)
        except Exception as e:
            logger.warning(f"Repair failed: {e}")
            return None

    def _safe_parse(self, code: str) -> Optional[schema.Module]:
        """Parse code with a repair loop."""
        for attempt in range(self.max_retries + 1):
            try:
                return self.parser.parse(code)
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Parse failed (attempt {attempt+1}/{self.max_retries+1}): {e}")
                    repaired_ir = self._repair_code(code, str(e))
                    if repaired_ir:
                        return repaired_ir
                    # If repair returned None, loop continues to try again or fail? 
                    # Actually _repair_code returns IR, so if it succeeds we are good.
                    # If it fails (returns None), we might want to try a different prompt or just give up.
                    # Here we just give up on this specific attempt but the loop continues?
                    # No, if _repair_code fails, we probably can't fix it.
                    break
                else:
                    logger.error(f"Final parse failed: {e}")
        return None

    def _mutate_with_prompt(self, code: str, system_prompt: str) -> Optional[schema.Module]:
        """Generic mutation helper with CoT and repair."""
        try:
            response = self.llm.complete(system_prompt).strip()
            optimized_code = self._clean_code(response)
            
            if optimized_code and optimized_code != code:
                return self._safe_parse(optimized_code)
        except Exception as e:
            logger.error(f"Mutation failed: {e}")
        return None

    def _mutate_idiomatic(self, code: str) -> Optional[schema.Module]:
        """Make code more Pythonic."""
        prompt = f"""You are an expert Python developer.
Refactor the following code to be more idiomatic and Pythonic.
Think step-by-step:
1. Identify non-idiomatic patterns (loops that could be comprehensions, manual counters, etc.).
2. Apply Pythonic replacements.
3. Verify correctness.

Return ONLY the Python code, no markdown, no explanations.

Code:
{code}
"""
        return self._mutate_with_prompt(code, prompt)
    
    def _mutate_library(self, code: str) -> Optional[schema.Module]:
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
        return self._mutate_with_prompt(code, prompt)
    
    def _mutate_algorithmic(self, code: str) -> Optional[schema.Module]:
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
        return self._mutate_with_prompt(code, prompt)
