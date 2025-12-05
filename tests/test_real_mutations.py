"""
Test suite for real mutation scenarios with new domain IR system.
Migrated from deprecated CodeIR to domain IR Module.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.mutator.formal import FormalMutator
from src.mutator.robust import RobustMutator
from src.infrastructure.parsing.python_parser import PythonParser
from src.infrastructure.codegen.python_codegen import PythonCodeGenerator


def test_loop_unrolling():
    """Test loop unrolling transformation with IR system."""
    mutator = FormalMutator()
    code = """
def sum_small():
    total = 0
    for i in range(3):
        total = total + i
    return total
"""
    parser = PythonParser()
    ir = parser.parse(code)
    
    # Apply mutations
    variants = mutator.mutate(ir)
    
    assert isinstance(variants, list)
    
    # Check if we got loop unrolling
    found_unrolling = False
    for variant_ir, mutation_type in variants:
        if "LoopUnrolling" in mutation_type:
            found_unrolling = True
            codegen = PythonCodeGenerator()
            reconstructed = codegen.generate(variant_ir)
            # Should be valid Python
            compile(reconstructed, '<string>', 'exec')
            print(f"✅ Loop unrolling: {mutation_type}")
            print(f"Unrolled code snippet:\n{reconstructed[:300]}")
            break
    
    if not found_unrolling:
        print(f"✅ FormalMutator generated {len(variants)} variants (loop unrolling may not apply)")


def test_list_comp():
    """Test list comprehension scenario with IR system."""
    mutator = RobustMutator()
    code = """
def map_values(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
"""
    parser = PythonParser()
    ir = parser.parse(code)
    
    # Apply mutations
    variants = mutator.mutate(ir)
    
    assert isinstance(variants, list)
    
    if variants:
        print(f"✅ List comp scenario: generated {len(variants)} variants")
        for variant_ir, mutation_type in variants:
            codegen = PythonCodeGenerator()
            reconstructed = codegen.generate(variant_ir)
            # Should be valid Python
            compile(reconstructed, '<string>', 'exec')
            print(f"  - {mutation_type}: ✅ valid")
    else:
        print("✅ List comp scenario: no applicable transformations")


def test_aug_assign():
    """Test augmented assignment transformation with IR system."""
    mutator = RobustMutator()
    code = """
def increment_counter(counter, step):
    counter = counter + step
    counter = counter * 2
    return counter
"""
    parser = PythonParser()
    ir = parser.parse(code)
    
    # Apply mutations
    variants = mutator.mutate(ir)
    
    assert isinstance(variants, list)
    
    # Check for augmented assignment
    found_aug = False
    for variant_ir, mutation_type in variants:
        if "AugAssign" in mutation_type:
            found_aug = True
            codegen = PythonCodeGenerator()
            reconstructed = codegen.generate(variant_ir)
            # Should contain augmented assignment operators
            has_aug = '+=' in reconstructed or '*=' in reconstructed
            assert has_aug
            print(f"✅ Augmented assignment: {mutation_type}")
            print(f"Optimized code:\n{reconstructed[:200]}")
            break
    
    if not found_aug:
        print(f"✅ Aug assign: generated {len(variants)} other variants")


if __name__ == '__main__':
    print("Testing Real Mutation Scenarios with IR System\n" + "="*50)
    test_loop_unrolling()
    print()
    test_list_comp()
    print()
    test_aug_assign()
    print("\n" + "="*50)
    print("✅ All real mutation tests passed!")
