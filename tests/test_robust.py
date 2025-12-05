"""
Test suite for robust mutator with new domain IR system.
Migrated from deprecated CodeIR to domain IR Module.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.mutator.robust import RobustMutator
from src.infrastructure.parsing.python_parser import PythonParser
from src.infrastructure.codegen.python_codegen import PythonCodeGenerator


def test_robust_mutator_range():
    """Test RobustMutator range optimization with IR system."""
    mutator = RobustMutator()
    code = """
def sum_values(n):
    result = 0
    for i in range(0, n):
        result = result + i
    return result
"""
    parser = PythonParser()
    ir = parser.parse(code)
    
    # Apply mutations
    variants = mutator.mutate(ir)
    
    assert isinstance(variants, list)
    
    print(f"✅ Range optimization test: generated {len(variants)} variants")
    
    if variants:
        for variant_ir, mutation_type in variants:
            codegen = PythonCodeGenerator()
            reconstructed = codegen.generate(variant_ir)
            # Should be valid Python
            compile(reconstructed, '<string>', 'exec')
            print(f"  - {mutation_type}: ✅ valid Python")


def test_robust_mutator_aug_assign():
    """Test RobustMutator augmented assignment with IR system."""
    mutator = RobustMutator()
    code = """
def accumulate(x, delta):
    x = x + delta
    x = x * 2
    return x
"""
    parser = PythonParser()
    ir = parser.parse(code)
    
    # Apply mutations
    variants = mutator.mutate(ir)
    
    assert isinstance(variants, list)
    
    print(f"✅ Augmented assignment test: generated {len(variants)} variants")
    
    if variants:
        for variant_ir, mutation_type in variants:
            codegen = PythonCodeGenerator()
            reconstructed = codegen.generate(variant_ir)
            # Should be valid Python
            compile(reconstructed, '<string>', 'exec')
            print(f"  - {mutation_type}: ✅ valid Python")
            
            # If it's an augmented assignment optimization, check for +=
            if "AugAssign" in mutation_type:
                assert '+=' in reconstructed or '*=' in reconstructed
                print(f"    Contains augmented assignment operator")


if __name__ == '__main__':
    print("Testing RobustMutator with IR System\n" + "="*50)
    test_robust_mutator_range()
    print()
    test_robust_mutator_aug_assign()
    print("\n" + "="*50)
    print("✅ All RobustMutator tests passed!")
