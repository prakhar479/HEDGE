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
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.parser = PythonParser()
        self.codegen = PythonCodeGenerator()
    
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
        if response.startswith("```python"):
            response = response.split("```python", 1)[1]
        elif response.startswith("```"):
            response = response.split("```", 1)[1]
        if response.endswith("```"):
            response = response.rsplit("```", 1)[0]
        return response.strip()
    
    def _mutate_idiomatic(self, code: str) -> Optional[schema.Module]:
        """Make code more Pythonic."""
        try:
            prompt = f"""You are an expert Python developer.
Refactor the following code to be more idiomatic and Pythonic.
Use list comprehensions, generator expressions, or built-in functions where appropriate.
Return ONLY the Python code, no markdown, no explanations.

Code:
{code}

Idiomatic Code:"""
            
            response = self.llm.complete(prompt).strip()
            optimized_code = self._clean_code(response)
            
            if optimized_code and optimized_code != code:
                return self.parser.parse(optimized_code)
        except Exception as e:
            logger.error(f"Idiomatic mutation failed: {e}")
        return None
    
    def _mutate_library(self, code: str) -> Optional[schema.Module]:
        """Replace manual implementations with standard library."""
        try:
            prompt = f"""You are an expert Python performance engineer.
Optimize the following code by replacing manual implementations with standard library functions.
Use itertools, collections, functools, or math where beneficial.
Return ONLY the Python code, no markdown, no explanations.

Code:
{code}

Optimized Code:"""
            
            response = self.llm.complete(prompt).strip()
            optimized_code = self._clean_code(response)
            
            if optimized_code and optimized_code != code:
                return self.parser.parse(optimized_code)
        except Exception as e:
            logger.error(f"Library mutation failed: {e}")
        return None
    
    def _mutate_algorithmic(self, code: str) -> Optional[schema.Module]:
        """Improve algorithmic complexity."""
        try:
            prompt = f"""You are an expert algorithm designer.
Analyze the following code and optimize its time or space complexity if possible.
Use better data structures or algorithms where appropriate.
Return ONLY the Python code, no markdown, no explanations.

Code:
{code}

Optimized Code:"""
            
            response = self.llm.complete(prompt).strip()
            optimized_code = self._clean_code(response)
            
            if optimized_code and optimized_code != code:
                return self.parser.parse(optimized_code)
        except Exception as e:
            logger.error(f"Algorithmic mutation failed: {e}")
        return None
