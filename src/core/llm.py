import logging
import os
from abc import ABC, abstractmethod
from typing import List, Optional

logger = logging.getLogger(__name__)

class LLMClient(ABC):
    @abstractmethod
    def complete(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        pass

class MockLLMClient(LLMClient):
    def complete(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        logger.info(f"MockLLM received prompt: {prompt[:50]}...")
        

        if "Summarize the algorithmic intent" in prompt or "Analyze the following Python code" in prompt:
            if "bubble_sort" in prompt or ("for i in range(n)" in prompt and "for j in range" in prompt):
                return "Sort a list of numbers in ascending order."
            if "fib_recursive" in prompt or "fib(n - 1) + fib(n - 2)" in prompt:
                return "Calculate the nth Fibonacci number using recursion."
            if "search_list" in prompt or "for i in range(len(items))" in prompt:
                return "Search for an element in a list and return its index."
            return "Perform a computation."


        if "Implement the following" in prompt or "Implement" in prompt:
            if "Sort a list of numbers" in prompt:
                # Return a better implementation (Merge Sort or Python's sorted)
                return """
def bubble_sort(arr):
    return sorted(arr)
"""
            if "Fibonacci" in prompt:
                if "dynamic programming" in prompt or "O(n)" in prompt:
                    # Optimized iterative version
                    return """
def fib_recursive(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
"""
                else:
                    # Basic version
                    return """
def fib(n):
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
"""
            if "Search for an element" in prompt:
                return """
def search_list(items, target):
    try:
        return items.index(target)
    except ValueError:
        return -1
"""
        

        if "Optimize the following algorithmic intent" in prompt:
            if "Sort a list of numbers" in prompt:
                return "Sort a list of numbers using an O(n log n) algorithm like Merge Sort or Quick Sort."
            if "Fibonacci" in prompt and "recursion" in prompt:
                return "Calculate the nth Fibonacci number using dynamic programming with O(n) time complexity."
            if "Search for an element" in prompt:
                return "Search for an element efficiently, consider using built-in methods."
        
        return ""

def get_llm_client() -> LLMClient:
    # Try OpenAI
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            from .llm_client import OpenAIClient
            logger.info("Using OpenAI Client")
            return OpenAIClient(api_key=openai_key)
        except ImportError:
            pass
            
    # Try Gemini
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            from .llm_client import GeminiClient
            logger.info("Using Gemini Client")
            return GeminiClient(api_key=gemini_key)
        except ImportError:
            pass

    # Fallback to Mock
    logger.warning("No valid API keys found (OPENAI_API_KEY or GEMINI_API_KEY). Using MockLLMClient.")
    return MockLLMClient()
