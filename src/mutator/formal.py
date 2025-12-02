import ast
import astor
import copy
from typing import List, Tuple
from .base import Mutator
from src.core.ir_manager import CodeIR, IRGenerator

class FormalMutator(Mutator):
    def __init__(self, llm_client=None):
        self.ir_generator = IRGenerator(llm_client)

    def mutate(self, code_ir: CodeIR) -> List[Tuple[CodeIR, str]]:
        """
        Applies formal AST transformations to original code, generates new IRs.
        """
        variants = []
        try:
            tree = ast.parse(code_ir.original_code)
        except SyntaxError:
            return []

        transformers = [
            (ConstantFoldingTransformer(), "Formal_ConstantFolding"),
            (DeadCodeEliminationTransformer(), "Formal_DCE"),
            (StrengthReductionTransformer(), "Formal_StrengthReduction"),
            (LoopUnrollingTransformer(), "Formal_LoopUnrolling")
        ]

        for transformer, name in transformers:
            new_tree = copy.deepcopy(tree)
            transformer.visit(new_tree)
            if transformer.mutated:
                try:
                    new_code = astor.to_source(new_tree)
                    # Generate new CodeIR for the transformed code
                    new_ir = self.ir_generator.generate_ir(new_code)
                    variants.append((new_ir, name))
                except Exception:
                    pass
        
        return variants

class ConstantFoldingTransformer(ast.NodeTransformer):
    def __init__(self):
        self.mutated = False

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
            try:
                # Safe evaluation of constant expressions
                left_val = node.left.value
                right_val = node.right.value
                if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
                    if isinstance(node.op, ast.Add):
                        val = left_val + right_val
                    elif isinstance(node.op, ast.Sub):
                        val = left_val - right_val
                    elif isinstance(node.op, ast.Mult):
                        val = left_val * right_val
                    elif isinstance(node.op, ast.Div) and right_val != 0:
                        val = left_val / right_val
                    else:
                        return node
                    
                    self.mutated = True
                    return ast.Constant(value=val)
            except Exception:
                pass
        return node

class DeadCodeEliminationTransformer(ast.NodeTransformer):
    def __init__(self):
        self.mutated = False

    def visit_If(self, node):
        self.generic_visit(node)
        # Check for "if False: ..." or "if 0: ..."
        if isinstance(node.test, ast.Constant) and not node.test.value:
            self.mutated = True
            # If there's an else block, replace the If with the else body
            if node.orelse:
                return node.orelse
            else:
                return [] # Remove the node entirely
        
        # Check for "if True: ..."
        if isinstance(node.test, ast.Constant) and node.test.value:
            self.mutated = True
            return node.body
            
        return node

class StrengthReductionTransformer(ast.NodeTransformer):
    def __init__(self):
        self.mutated = False

    def visit_BinOp(self, node):
        self.generic_visit(node)
        # x ** 2 -> x * x
        if isinstance(node.op, ast.Pow) and isinstance(node.right, ast.Constant) and node.right.value == 2:
            self.mutated = True
            return ast.BinOp(
                left=node.left,
                op=ast.Mult(),
                right=node.left
            )
        return node

class LoopUnrollingTransformer(ast.NodeTransformer):
    def __init__(self):
        self.mutated = False

    def visit_For(self, node):
        # Only unroll small constant loops like "for i in range(3):"
        if (isinstance(node.iter, ast.Call) and 
            isinstance(node.iter.func, ast.Name) and 
            node.iter.func.id == 'range' and
            len(node.iter.args) == 1 and
            isinstance(node.iter.args[0], ast.Constant) and
            isinstance(node.iter.args[0].value, int) and
            node.iter.args[0].value <= 5): # Limit unrolling to small loops
            
            limit = node.iter.args[0].value
            new_body = []
            
            for i in range(limit):
                # Create a copy of the body
                iteration_body = copy.deepcopy(node.body)
                
                # Replace loop variable with constant i
                if isinstance(node.target, ast.Name):
                    loop_var_name = node.target.id
                    
                    class VarReplacer(ast.NodeTransformer):
                        def visit_Name(self, n):
                            if n.id == loop_var_name and isinstance(n.ctx, ast.Load):
                                return ast.Constant(value=i)
                            return n
                            
                    for stmt in iteration_body:
                        VarReplacer().visit(stmt)
                
                new_body.extend(iteration_body)
            
            self.mutated = True
            return new_body
            
        return self.generic_visit(node)
