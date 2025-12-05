import logging
from .llm import LLMClient

logger = logging.getLogger(__name__)

class AbstractionManager:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def lift(self, code: str) -> str:
        prompt = f"""You are an expert computer scientist analyzing code for optimization.

Analyze the following Python code and provide a concise algorithmic summary.
Focus on WHAT it does (the algorithm), not HOW (implementation details).
Describe the time complexity if relevant.
Provide ONLY the intent summary, no explanations or extra text.

Code:
{code}

Algorithmic Intent:"""
        return self.llm.complete(prompt).strip()

    def lower(self, intent: str) -> str:
        prompt = f"""You are an expert Python programmer specializing in high-performance code.

Implement the following algorithmic intent in efficient, production-ready Python code.
- Use the most efficient algorithm and data structures
- Preserve the original function signature if it's implied in the intent
- Return ONLY the Python code, no markdown formatting, no explanations

Intent:
{intent}

Python Code:"""
        code = self.llm.complete(prompt).strip()
        
        # Clean up markdown formatting if present
        if code.startswith("```python"):
            code = code.split("```python")[1]
        elif code.startswith("```"):
            code = code.split("```")[1]
        if code.endswith("```"):
            code = code.rsplit("```", 1)[0]
        
        return code.strip()
