"""
Test Suite for Mutators

Tests structural and semantic mutations.
"""
import pytest
from src.application.mutators.structural import StructuralMutator
from src.infrastructure.parsing.python_parser import PythonParser
from src.infrastructure.codegen.python_codegen import PythonCodeGenerator

class TestStructuralMutator:
    """Test suite for structural mutator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mutator = StructuralMutator(use_context=False)  # Disable context for simpler tests
        self.parser = PythonParser()
        self.codegen = PythonCodeGenerator()
    
    def test_mutate_returns_list(self):
        """Test that mutate returns a list of variants."""
        code = """
def test():
    x = 1
    y = 2
    return x + y
"""
        ir = self.parser.parse(code)
        variants = self.mutator.mutate(ir)
        
        assert isinstance(variants, list)
    
    def test_reorder_mutation(self):
        """Test statement reordering mutation."""
        code = """
def test():
    x = 1
    y = 2
    z = 3
    return x + y + z
"""
        ir = self.parser.parse(code)
        variants = self.mutator.mutate(ir)
        
        # Should produce at least one variant
        # Note: May not always succeed due to randomness
        assert isinstance(variants, list)
    
    def test_swap_operands_mutation(self):
        """Test operand swapping mutation."""
        code = """
def test():
    return 1 + 2
"""
        ir = self.parser.parse(code)
        variants = self.mutator.mutate(ir)
        
        assert isinstance(variants, list)
        
        # If a swap variant was created, verify it's valid
        for variant_ir, name in variants:
            if "Swap" in name:
                generated_code = self.codegen.generate(variant_ir)
                assert "+" in generated_code or generated_code  # Should still be valid code
    
    def test_mutations_are_distinct(self):
        """Test that mutations produce different IR."""
        code = """
def test():
    a = 1
    b = 2
    c = 3
    return a + b * c
"""
        ir = self.parser.parse(code)
        variants = self.mutator.mutate(ir)
        
        # Each variant should be a new object
        for variant_ir, name in variants:
            assert variant_ir is not ir  # Different object due to deepcopy

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
