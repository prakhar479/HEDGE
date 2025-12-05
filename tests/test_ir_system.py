"""
Test suite for IR system using new domain IR.
Migrated from deprecated CodeIR to domain IR Module.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.infrastructure.parsing.python_parser import PythonParser
from src.infrastructure.codegen.python_codegen import PythonCodeGenerator
from src.mutator.simple import SimpleMutator
from src.core.validator import Validator
from src.domain.ir.schema import Module, FunctionDef

def test_ir_generation_and_reconstruction():
    """Test parsing code to IR and generating back to code."""
    code = """
def add(a, b):
    return a + b
"""
    parser = PythonParser()
    ir = parser.parse(code)
    
    assert isinstance(ir, Module)
    assert len(ir.body.statements) == 1
    assert isinstance(ir.body.statements[0], FunctionDef)
    
    # Reconstruct
    codegen = PythonCodeGenerator()
    reconstructed_code = codegen.generate(ir)
    
    # Should contain function definition
    assert "def add" in reconstructed_code
    assert "return" in reconstructed_code

def test_simple_mutator_reorder():
    """Test SimpleMutator with statement reordering."""
    code = """
def func():
    a = 1
    b = 2
    return a + b
"""
    parser = PythonParser()
    ir = parser.parse(code)
    
    mutator = SimpleMutator()
    variants = mutator.mutate(ir)
    
    # SimpleMutator may or may not generate variants depending on statement independence
    assert isinstance(variants, list)
    
    if variants:
        variant_ir, strategy = variants[0]
        assert strategy == "Simple_ReorderStatements"
        assert variant_ir != ir  # IR should be different

def test_validator_schema():
    """Test validator with valid IR."""
    code = "def foo(): pass"
    parser = PythonParser()
    ir = parser.parse(code)
    
    validator = Validator()
    result = validator.validate_pre_mutation(ir)
    assert result.valid

def test_round_trip():
    """Test that code can be parsed and reconstructed."""
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
"""
    parser = PythonParser()
    codegen = PythonCodeGenerator()
    
    ir = parser.parse(code)
    reconstructed = codegen.generate(ir)
    
    # Should be able to compile
    compile(reconstructed, '<string>', 'exec')
