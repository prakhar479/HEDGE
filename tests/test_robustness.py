import pytest
from src.mutator.simple import SimpleMutator
from src.core.engine import EvolutionaryEngine
from src.green_gym.runner import CodeRunner
from src.mutator.base import Mutator
from typing import List

class EmptyMutator(Mutator):
    def mutate(self, code_str: str) -> List[str]:
        return []

def test_simple_mutator_no_op():
    mutator = SimpleMutator()
    code = """
def add(a, b):
    return a + b
"""
    variants = mutator.mutate(code)
    # Should be empty because 'add' is not 'bubble_sort' or 'fib_recursive'
    assert variants == []

def test_engine_no_variants():
    runner = CodeRunner()
    mutator = EmptyMutator()
    engine = EvolutionaryEngine([mutator], runner, generations=2)
    
    code = "def foo(): pass"
    test_code = "def test(): pass"
    
    best_code, metrics = engine.optimize(code, test_code)
    
    # Should return original code
    assert best_code == code
    # Should have baseline metrics
    assert "duration_seconds" in metrics

def test_engine_baseline_failure():
    runner = CodeRunner()
    mutator = EmptyMutator()
    engine = EvolutionaryEngine([mutator], runner)
    
    code = "def foo(): raise Exception('fail')"
    test_code = "def test(): candidate.foo()"
    
    best_code, metrics = engine.optimize(code, test_code)
    
    assert "error" in metrics
    assert metrics["error"] == "Baseline failed"
