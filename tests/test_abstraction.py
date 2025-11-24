from src.core.llm import MockLLMClient
from src.core.abstraction import AbstractionManager
from src.mutator.llm_mutator import LLMMutator

def test_abstraction_lift_lower():
    client = MockLLMClient()
    manager = AbstractionManager(client)
    
    code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        pass
"""
    intent = manager.lift(code)
    assert "Sort a list of numbers" in intent
    
    new_code = manager.lower(intent)
    assert "sorted(arr)" in new_code

def test_llm_mutator():
    client = MockLLMClient()
    manager = AbstractionManager(client)
    mutator = LLMMutator(client, manager)
    
    code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        pass
"""
    variants = mutator.mutate(code)
    assert len(variants) > 0
    # The mock should return the sorted() version via L1 optimization
    assert "sorted(arr)" in variants[0]
