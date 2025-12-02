import ast
import astor
import random
import copy
from typing import List, Tuple
from .base import Mutator

class SimpleMutator(Mutator):
    def __init__(self):
        pass

    def mutate(self, code_str: str) -> List[Tuple[str, str]]:
        """
        Applies random AST transformations to generate variants.
        """
        variants = []
        
        try:
            tree = ast.parse(code_str)
        except SyntaxError:
            return []

        # List of available transformers
        transformers = [
            (LoopUnrollingTransformer(), "Simple_LoopUnrolling"),
            (ListCompTransformer(), "Simple_ListComp"),
            (AugAssignTransformer(), "Simple_AugAssign")
        ]
        
        # Apply each transformer to a fresh copy of the tree
        for transformer, name in transformers:
            new_tree = copy.deepcopy(tree)
            transformer.visit(new_tree)
            if transformer.mutated:
                variants.append((astor.to_source(new_tree), name))
            
        return variants

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
            
            # Very simple unrolling: just duplicate the body 'limit' times
            # Note: This doesn't handle the loop variable 'i' substitution yet for simplicity,
            # but for simple "do X times" loops it works.
            # To do it properly, we'd need to replace references to the loop var with the constant.
            
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

class ListCompTransformer(ast.NodeTransformer):
    def __init__(self):
        self.mutated = False

    def visit_For(self, node):
        # Look for pattern:
        # result = []
        # for x in iterable:
        #     result.append(transformation(x))
        
        # This is a bit complex to match perfectly in a simple transformer without looking at parent context.
        # Simplified version: Look for a for loop where the only statement is an append.
        
        if (len(node.body) == 1 and 
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Call) and
            isinstance(node.body[0].value.func, ast.Attribute) and
            node.body[0].value.func.attr == 'append'):
            
            # Found a loop with a single append
            # Construct list comprehension: [append_arg for target in iter]
            
            append_call = node.body[0].value
            if len(append_call.args) == 1:
                elt = append_call.args[0]
                target = node.target
                iterator = node.iter
                
                # We can't easily replace the whole loop + initialization without parent context.
                # But we can replace the loop with: target_list.extend([elt for target in iterator])
                # Or if we assume the user code is simple.
                
                # Let's try to replace the loop with an extend call which is slightly faster than repeated appends
                # target_list.extend([elt for target in iterator])
                
                target_list = append_call.func.value
                
                list_comp = ast.ListComp(elt=elt, generators=[ast.comprehension(target=target, iter=iterator, ifs=[], is_async=0)])
                
                new_node = ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(value=target_list, attr='extend', ctx=ast.Load()),
                        args=[list_comp],
                        keywords=[]
                    )
                )
                
                self.mutated = True
                return new_node
                
        return self.generic_visit(node)

class AugAssignTransformer(ast.NodeTransformer):
    def __init__(self):
        self.mutated = False

    def visit_Assign(self, node):
        # Look for x = x + 1 -> x += 1
        if (len(node.targets) == 1 and 
            isinstance(node.targets[0], ast.Name) and
            isinstance(node.value, ast.BinOp) and
            isinstance(node.value.left, ast.Name) and
            node.value.left.id == node.targets[0].id):
            
            # It's x = x op y
            op = node.value.op
            rhs = node.value.right
            
            new_node = ast.AugAssign(
                target=node.targets[0],
                op=op,
                value=rhs
            )
            
            self.mutated = True
            return new_node
            
        return self.generic_visit(node)
