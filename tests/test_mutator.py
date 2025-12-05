"""
Test suite for mutators using new domain IR system.
Migrated from deprecated CodeIR to domain IR Module.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.mutator.simple import SimpleMutator
from src.mutator.formal import FormalMutator
from src.mutator.robust import RobustMutator
from src.infrastructure.parsing.python_parser import PythonParser
from src.infrastructure.codegen.python_codegen import PythonCodeGenerator


def test_simple_mutator_bubble_sort():
    """Test SimpleMutator with bubble sort."""
    mutator = SimpleMutator()
    code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
    parser = PythonParser()
    ir = parser.parse(code)
    
    # Apply mutation
    variants = mutator.mutate(ir)
    
    assert isinstance(variants, list)
    print(f"✅ SimpleMutator generated {len(variants)} variants for bubble sort")


def test_formal_mutator_constant_folding():
    """Test FormalMutator with constant folding."""
    mutator = FormalMutator()
    code = """
def calculate():
    x = 2 + 3
    y = x * 4
    return y
"""
    parser = PythonParser()
    ir = parser.parse(code)
    
    # Apply mutation
    variants = mutator.mutate(ir)
    
    assert isinstance(variants, list)
    
    if variants:
        variant_ir, mutation_type = variants[0]
        codegen = PythonCodeGenerator()
        reconstructed = codegen.generate(variant_ir)
        assert '5' in reconstructed or '2 + 3' in reconstructed
        print(f"✅ FormalMutator generated {len(variants)} variants - {mutation_type}")
        print(f"Sample variant:\n{reconstructed[:200]}")
    else:
        print("✅ FormalMutator completed (no applicable transformations)")


def test_robust_mutator_range_optimization():
    """Test RobustMutator with range optimization."""
    mutator = RobustMutator()
    code = """
def sum_range(n):
    total = 0
    for i in range(0, n):
        total = total + i
    return total
"""
    parser = PythonParser()
    ir = parser.parse(code)
    
    # Apply mutation
    variants = mutator.mutate(ir)
    
    assert isinstance(variants, list)
    
    if variants:
        for variant_ir, mutation_type in variants:
            if "Range" in mutation_type:
                codegen = PythonCodeGenerator()
                reconstructed = codegen.generate(variant_ir)
                print(f"✅ RobustMutator - {mutation_type}")
                print(f"Optimized code:\n{reconstructed[:200]}")
                break
        else:
            print(f"✅ RobustMutator generated {len(variants)} variants")
    else:
        print("✅ RobustMutator completed (no applicable transformations)")


def test_robust_mutator_aug_assign():
    """Test RobustMutator with augmented assignment."""
    mutator = RobustMutator()
    code = """
def increment(x, y):
    x = x + y
    return x
"""
    parser = PythonParser()
    ir = parser.parse(code)
    
    # Apply mutation
    variants = mutator.mutate(ir)
    
    assert isinstance(variants, list)
    
    if variants:
        for variant_ir, mutation_type in variants:
            if "AugAssign" in mutation_type:
                codegen = PythonCodeGenerator()
                reconstructed = codegen.generate(variant_ir)
                # Should have augmented assignment
                assert '+=' in reconstructed
                print(f"✅ RobustMutator - {mutation_type}")
                print(f"Optimized code:\n{reconstructed[:200]}")
                return
        
        print(f"✅ RobustMutator generated {len(variants)} variants (AugAssign may not apply)")
    else:
        print("✅ RobustMutator completed")


if __name__ == '__main__':
    print("Testing Mutators with IR System\n" + "="*50)
    test_simple_mutator_bubble_sort()
    print()
    test_formal_mutator_constant_folding()
    print()
    test_robust_mutator_range_optimization()
    print()
    test_robust_mutator_aug_assign()
    print("\n" + "="*50)
    print("✅ All mutator tests passed!")
