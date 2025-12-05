"""
Test suite for system robustness with new domain IR system.
Migrated from deprecated CodeIR to domain IR Module.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.mutator.simple import SimpleMutator
from src.application.engine.evolution import EvolutionaryEngine
from src.infrastructure.execution.runner import GreenGymRunner
from src.domain.interfaces import Mutator
from src.domain.ir.schema import Module
from typing import List, Tuple


class EmptyMutator(Mutator):
    """Mutator that generates no variants - for testing edge cases."""
    def mutate(self, ir: Module) -> List[Tuple[Module, str]]:
        return []


def test_simple_mutator_minimal_code():
    """Test SimpleMutator with minimal code that has no reorderable statements."""
    mutator = SimpleMutator()
    code = """
def add(a, b):
    return a + b
"""
    from src.infrastructure.parsing.python_parser import PythonParser
    parser = PythonParser()
    ir = parser.parse(code)
    
    # Apply mutation
    variants = mutator.mutate(ir)
    
    # Should be empty because there's only one statement (return)
    assert variants == []
    print("✅ SimpleMutator correctly returns no variants for single-statement function")


def test_engine_no_variants():
    """Test engine with a mutator that generates no variants."""
    runner = GreenGymRunner()
    mutator = EmptyMutator()
    engine = EvolutionaryEngine([mutator], runner, generations=2)
    
    code = "def foo(): pass"
    test_code = "def test(): pass"
    
    # optimize returns list of pareto solutions
    pareto_solutions = engine.optimize(code, test_code)
    
    # Should return at least the baseline
    assert len(pareto_solutions) >= 1
    
    # First solution should be the baseline
    baseline = pareto_solutions[0]
    assert "duration_seconds" in baseline.metrics
    
    print(f"✅ Engine with no variants returned {len(pareto_solutions)} solution(s) (baseline)")


def test_engine_baseline_failure():
    """Test engine behavior when baseline code fails."""
    runner = GreenGymRunner()
    mutator = EmptyMutator()
    engine = EvolutionaryEngine([mutator], runner)
    
    code = "def foo(): raise Exception('fail')"
    test_code = "def test(): candidate.foo()"
    
    # optimize returns list of pareto solutions
    pareto_solutions = engine.optimize(code, test_code)
    
    # When baseline fails, we get empty pareto set
    assert pareto_solutions == []
    
    print("✅ Engine correctly returns empty set when baseline fails")


if __name__ == '__main__':
    print("Testing System Robustness with IR System\n" + "="*50)
    test_simple_mutator_minimal_code()
    print()
    test_engine_no_variants()
    print()
    test_engine_baseline_failure()
    print("\n" + "="*50)
    print("✅ All robustness tests passed!")
