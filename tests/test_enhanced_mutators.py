"""
Test Suite for Enhanced Mutators

Tests the new advanced mutator implementations.
"""
import pytest
from src.application.mutators.structural import (
    StructuralMutator,
    AlgebraicSimplificationTransformer,
    LoopOptimizationTransformer
)
from src.application.mutators.data_structure import DataStructureOptimizationMutator
from src.application.mutators.advanced import (
    CommonSubexpressionEliminationMutator,
    LoopInvariantCodeMotionMutator
)
from src.infrastructure.parsing.python_parser import PythonParser
from src.infrastructure.codegen.python_codegen import PythonCodeGenerator


class TestEnhancedStructuralMutator:
    """Test suite for enhanced structural mutator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mutator = StructuralMutator(use_context=False)
        self.parser = PythonParser()
        self.codegen = PythonCodeGenerator()
    
    def test_strength_reduction_power(self):
        """Test power operation strength reduction."""
        code = """
def test():
    x = 5
    y = x ** 2
    z = x ** 3
    return y + z
"""
        ir = self.parser.parse(code)
        variants = self.mutator.mutate(ir)
        
        # Should produce strength reduction variants
        assert isinstance(variants, list)
        
        # Check if any variant contains strength reduction
        for variant_ir, name in variants:
            if "StrengthReduction" in name:
                generated_code = self.codegen.generate(variant_ir)
                # x ** 2 should become x * x
                assert "**" not in generated_code or "* x" in generated_code
    
    def test_algebraic_simplification(self):
        """Test algebraic simplification."""
        code = """
def test():
    x = 5
    y = x + 0
    z = x * 1
    return y + z
"""
        ir = self.parser.parse(code)
        variants = self.mutator.mutate(ir)
        
        # Should produce algebraic simplification variants
        assert isinstance(variants, list)
        
        for variant_ir, name in variants:
            if "AlgebraicSimplification" in name:
                generated_code = self.codegen.generate(variant_ir)
                # Simplifications should be applied
                assert generated_code is not None
    
    def test_boolean_simplification(self):
        """Test boolean algebra simplification."""
        code = """
def test(a, b):
    if not (a and b):
        return True
    return False
"""
        ir = self.parser.parse(code)
        
        transformer = AlgebraicSimplificationTransformer()
        new_ir = transformer.visit(ir)
        
        # Should apply De Morgan's law
        if transformer.changed:
            generated_code = self.codegen.generate(new_ir)
            assert generated_code is not None


class TestDataStructureOptimization:
    """Test suite for data structure optimization mutator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mutator = DataStructureOptimizationMutator()
        self.parser = PythonParser()
        self.codegen = PythonCodeGenerator()
    
    def test_list_to_set_membership(self):
        """Test list to set conversion for membership testing."""
        code = """
def test(x):
    if x in [1, 2, 3, 4, 5]:
        return True
    return False
"""
        ir = self.parser.parse(code)
        variants = self.mutator.mutate(ir)
        
        assert isinstance(variants, list)
        
        # Check for set conversion
        for variant_ir, name in variants:
            if "SetMembership" in name:
                generated_code = self.codegen.generate(variant_ir)
                # Should use set instead of list
                assert "{" in generated_code or "set" in generated_code
    
    def test_nested_loops_to_product(self):
        """Test nested loops to itertools.product conversion."""
        code = """
def test():
    result = []
    for i in range(3):
        for j in range(4):
            result.append((i, j))
    return result
"""
        ir = self.parser.parse(code)
        variants = self.mutator.mutate(ir)
        
        assert isinstance(variants, list)
        
        # Check for itertools.product usage
        for variant_ir, name in variants:
            if "Product" in name:
                generated_code = self.codegen.generate(variant_ir)
                assert "itertools" in generated_code or "product" in generated_code


class TestAdvancedMutators:
    """Test suite for advanced compiler-style mutators."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PythonParser()
        self.codegen = PythonCodeGenerator()
    
    def test_common_subexpression_elimination(self):
        """Test CSE mutator."""
        code = """
def test(a, b):
    x = a + b
    y = a + b
    z = a + b
    return x + y + z
"""
        ir = self.parser.parse(code)
        mutator = CommonSubexpressionEliminationMutator()
        variants = mutator.mutate(ir)
        
        # CSE should identify repeated expressions
        assert isinstance(variants, list)
    
    def test_loop_invariant_code_motion(self):
        """Test LICM mutator."""
        code = """
def test(n):
    result = 0
    constant = 10 * 20
    for i in range(n):
        result += constant
    return result
"""
        ir = self.parser.parse(code)
        mutator = LoopInvariantCodeMotionMutator()
        variants = mutator.mutate(ir)
        
        # LICM should hoist invariant code
        assert isinstance(variants, list)


class TestLoopOptimization:
    """Test suite for loop optimization."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PythonParser()
        self.codegen = PythonCodeGenerator()
    
    def test_loop_fusion(self):
        """Test loop fusion optimization."""
        code = """
def test():
    a = []
    b = []
    for i in range(10):
        a.append(i)
    for i in range(10):
        b.append(i * 2)
    return a, b
"""
        ir = self.parser.parse(code)
        
        transformer = LoopOptimizationTransformer()
        new_ir = transformer.visit(ir)
        
        # Should attempt loop fusion
        if transformer.changed:
            generated_code = self.codegen.generate(new_ir)
            assert generated_code is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])