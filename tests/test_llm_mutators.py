
import pytest
from unittest.mock import MagicMock
from src.application.mutators.semantic import SemanticMutator
from src.application.mutators.syntactic import SyntacticReasoningMutator
from src.application.mutators.external import ExternalLibraryMutator
from src.domain.ir import schema

class TestLLMMutators:
    
    def test_syntactic_mutation(self):
        # Initial: loops
        ir = schema.Module(body=schema.Block(statements=[schema.Pass()]))
        
        # Mock LLM returning list compr
        mock_llm = MagicMock()
        code_resp = "x = [i for i in range(10)]"
        mock_llm.complete.return_value = f"```python\n{code_resp}\n```"
        
        mutator = SyntacticReasoningMutator(llm_client=mock_llm)
        mutator.codegen.generate = MagicMock(return_value="x = []\nfor i in range(10): x.append(i)")
        # Mock parsing:
        parsed_ir = schema.Module(body=schema.Block(statements=[
             schema.Assign(targets=[schema.Name(id="x")], value=schema.ListExpr(elts=[])) 
        ])) 
        # Actually simplified mocking: just trust _safe_parse call if we mock parsing logic? 
        # Easier to integration test or just trust the logic if we mock parsers.
        # But here I want to test the *Logic* of the mutator class.
        
        # Let's mock _safe_parse directly to return a valid IR
        mutator._safe_parse = MagicMock(return_value=parsed_ir)
        mutator._get_imports = MagicMock(return_value=set()) # No new imports
        
        variants = mutator.mutate(ir)
        assert len(variants) > 0
        assert variants[0][1] == "Syntactic_Comprehensions"

    def test_external_mutation_allows_numpy(self):
        ir = schema.Module(body=schema.Block(statements=[schema.Pass()]))
        mock_llm = MagicMock()
        mock_llm.complete.return_value = "import numpy as np"
        
        mutator = ExternalLibraryMutator(llm_client=mock_llm)
        mutator.codegen.generate = MagicMock(return_value="pass")
        
        # Mock parser returning IR with numpy import
        new_ir = schema.Module(body=schema.Block(statements=[
            schema.Import(names=[schema.Alias(name="numpy", asname="np")])
        ]))
        mutator._safe_parse = MagicMock(return_value=new_ir)
        
        # Should be accepted
        variants = mutator.mutate(ir)
        assert len(variants) > 0
        assert variants[0][1] == "External_Vectorization"

    def test_stdlib_mutation_rejects_numpy(self):
        ir = schema.Module(body=schema.Block(statements=[schema.Pass()]))
        mock_llm = MagicMock()
        mock_llm.complete.return_value = "import numpy as np"
        
        mutator = SemanticMutator(llm_client=mock_llm)
        mutator.codegen.generate = MagicMock(return_value="pass")
        
        # Mock parser returning IR with numpy import
        new_ir = schema.Module(body=schema.Block(statements=[
            schema.Import(names=[schema.Alias(name="numpy", asname="np")])
        ]))
        mutator._safe_parse = MagicMock(return_value=new_ir)
        
        # We generally shouldn't mock inner methods like _get_imports if we want to test validation logic
        # But we need to ensure the FIRST call (on original IR) returns empty set, 
        # and SECOND call (on new IR) returns numpy.
        
        # Real _get_imports works on schema nodes, so it should just work if we pass real nodes.
        # But our input 'ir' has 'Pass', so imports is empty.
        # Our new_ir has 'Import numpy', so imports is {'numpy'}.
        
        # Should be REJECTED because SemanticMutator is StdLib only
        variants = mutator.mutate(ir)
        assert len(variants) == 0
