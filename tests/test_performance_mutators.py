
import pytest
from src.domain.ir import schema
from src.application.mutators.advanced import (
    ConstantFoldingMutator, 
    DeadCodeEliminationMutator,
    LoopUnrollingMutator
)
from src.application.mutators.structural import (
    StrengthReductionTransformer, 
    FastMembershipTransformer
)

class TestPerformanceMutators:
    
    def test_constant_folding(self):
        # 2 + 3 -> 5
        ir = schema.Module(body=schema.Block(statements=[
            schema.ExprStmt(value=schema.BinaryOp(
                left=schema.Constant(value=2, kind="int"),
                op="+",
                right=schema.Constant(value=3, kind="int")
            ))
        ]))
        
        mutator = ConstantFoldingMutator()
        variants = mutator.mutate(ir)
        assert len(variants) == 1
        new_ir = variants[0][0]
        expr = new_ir.body.statements[0].value
        assert isinstance(expr, schema.Constant)
        assert expr.value == 5
        
    def test_dead_code_elimination(self):
        # return; a = 1
        ir = schema.Module(body=schema.Block(statements=[
            schema.Return(value=None),
            schema.Assign(targets=[schema.Name(id="a")], value=schema.Constant(value=1, kind="int"))
        ]))
        
        mutator = DeadCodeEliminationMutator()
        variants = mutator.mutate(ir)
        assert len(variants) == 1
        new_ir = variants[0][0]
        assert len(new_ir.body.statements) == 1
        assert isinstance(new_ir.body.statements[0], schema.Return)

    def test_strength_reduction_transformer(self):
        # x ** 2 -> x * x
        binop = schema.BinaryOp(
            left=schema.Name(id="x"),
            op="**",
            right=schema.Constant(value=2, kind="int")
        )
        
        transformer = StrengthReductionTransformer()
        new_node = transformer.visit_BinaryOp(binop)
        
        assert new_node.op == "*"
        assert new_node.right == new_node.left  # Should be x * x

    def test_fast_membership_transformer(self):
        # x in [1, 2] -> x in {1, 2}
        compare = schema.Compare(
            left=schema.Name(id="x"),
            ops=["in"],
            comparators=[schema.ListExpr(elts=[
                schema.Constant(value=1, kind="int"),
                schema.Constant(value=2, kind="int")
            ])]
        )
        
        transformer = FastMembershipTransformer()
        new_node = transformer.visit_Compare(compare)
        
        assert isinstance(new_node.comparators[0], schema.SetExpr)
