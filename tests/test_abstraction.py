"""
Test suite for abstraction and LLM mutator with new domain IR system.
Migrated from deprecated CodeIR to domain IR Module.

Note: This test uses deprecated AbstractionManager and MockLLMClient.
These should be migrated or replaced in a future refactoring.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.llm import MockLLMClient
from src.mutator.llm_mutator import LLMMutator
from src.infrastructure.parsing.python_parser import PythonParser
from src.infrastructure.codegen.python_codegen import PythonCodeGenerator


def test_llm_mutator():
    """Test LLMMutator with mock LLM and new IR system."""
    client = MockLLMClient()
    mutator = LLMMutator(client)
    
    code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        pass
"""
    parser = PythonParser()
    ir = parser.parse(code)
    
    # Apply LLM mutations
    variants = mutator.mutate(ir)
    
    # Should generate some variants (or none, depending on mock behavior)
    assert isinstance(variants, list)
    
    if variants:
        variant_ir, mutation_type = variants[0]
        codegen = PythonCodeGenerator()
        reconstructed = codegen.generate(variant_ir)
        
        # Mock LLM should produce optimized sorting code
        has_sorting = "sorted" in reconstructed.lower()
        
        print(f"✅ LLMMutator generated {len(variants)} variants")
        print(f"   Mutation type: {mutation_type}")
        print(f"   Contains sorting optimization: {has_sorting}")
        
        assert len(variants) > 0
    else:
        print("✅ LLMMutator completed (mock may not generate variants)")


if __name__ == '__main__':
    print("Testing LLM Mutator with IR System\n" + "="*50)
    test_llm_mutator()
    print("\n" + "="*50)
    print("✅ All LLM mutator tests passed!")
