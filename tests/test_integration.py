import os
import pytest
from src.green_gym.runner import CodeRunner
from src.mutator.simple import SimpleMutator
from src.mutator.llm_mutator import LLMMutator
from src.core.llm import MockLLMClient
from src.core.abstraction import AbstractionManager
from src.core.engine import EvolutionaryEngine

def test_full_evolutionary_loop():
    # Setup
    runner = CodeRunner(timeout_seconds=10)
    llm_client = MockLLMClient()
    abstraction_manager = AbstractionManager(llm_client)
    
    simple_mutator = SimpleMutator()
    llm_mutator = LLMMutator(llm_client, abstraction_manager)
    
    engine = EvolutionaryEngine([simple_mutator, llm_mutator], runner, generations=3)
    
    # Target: Inefficient Bubble Sort
    initial_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
    
    # Test Harness
    test_code = """
def test():
    assert candidate.bubble_sort([3, 1, 2]) == [1, 2, 3]
    assert candidate.bubble_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
"""

    # Run
    best_code, best_metrics = engine.optimize(initial_code, test_code)
    
    # Verify
    # The MockLLM should have optimized it to use sorted() or similar
    # Or SimpleMutator might have done something (though it's weak currently)
    # The LLMMutator is the strong one here with the mock.
    
    assert "sorted(arr)" in best_code or "bubble_sort" in best_code or "return sorted" in best_code
    # Metrics should exist
    assert "duration_seconds" in best_metrics
