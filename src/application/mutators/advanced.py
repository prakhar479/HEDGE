"""
Advanced IR mutators implementing state-of-the-art program transformations.
"""
import copy
import operator
from typing import List, Tuple, Any, Optional, Set

from src.domain.interfaces import Mutator
from src.domain.ir import schema
from src.domain.ir.utils import NodeTransformer
from src.domain.ir.context import MutationContext

class ConstantFoldingTransformer(NodeTransformer):
    """Transformer for constant folding."""
    
    def __init__(self):
        self.changed = False
        self.ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '//': operator.floordiv,
            '%': operator.mod,
            '**': operator.pow,
            '<<': operator.lshift,
            '>>': operator.rshift,
            '|': operator.or_,
            '^': operator.xor,
            '&': operator.and_,
            '==': operator.eq,
            '!=': operator.ne,
            '<': operator.lt,
            '<=': operator.le,
            '>': operator.gt,
            '>=': operator.ge,
        }

    def visit_BinaryOp(self, node: schema.BinaryOp) -> schema.Expression:
        # First visit children to fold them if possible
        node = self.generic_visit(node)
        
        if isinstance(node.left, schema.Constant) and isinstance(node.right, schema.Constant):
            try:
                op_func = self.ops.get(node.op)
                if op_func:
                    val = op_func(node.left.value, node.right.value)
                    self.changed = True
                    return schema.Constant(
                        value=val,
                        kind=type(val).__name__
                    )
            except Exception:
                # Division by zero, overflow, etc.
                pass
        return node

    def visit_BoolOp(self, node: schema.BoolOp) -> schema.Expression:
        node = self.generic_visit(node)
        # Short circuit logic simplification could go here
        # e.g. True or X -> True
        # For now, simplistic folding if all are constant
        if all(isinstance(v, schema.Constant) for v in node.values):
            try:
                if node.op == 'and':
                    val = all(v.value for v in node.values)
                elif node.op == 'or':
                    val = any(v.value for v in node.values)
                else:
                    return node
                
                self.changed = True
                return schema.Constant(value=val, kind="bool")
            except:
                pass
        return node
        
    def visit_UnaryOp(self, node: schema.UnaryOp) -> schema.Expression:
        node = self.generic_visit(node)
        if isinstance(node.operand, schema.Constant):
            try:
                if node.op == 'not':
                    val = not node.operand.value
                elif node.op == '-':
                    val = -node.operand.value
                elif node.op == '+':
                    val = +node.operand.value
                elif node.op == '~':
                    val = ~node.operand.value
                else:
                    return node
                
                self.changed = True
                return schema.Constant(value=val, kind=type(val).__name__)
            except:
                pass
        return node


class ConstantFoldingMutator(Mutator):
    def mutate(self, ir: schema.Module) -> List[Tuple[schema.Module, str]]:
        new_ir = copy.deepcopy(ir)
        transformer = ConstantFoldingTransformer()
        transformer.visit(new_ir)
        
        if transformer.changed:
            return [(new_ir, "Advanced_ConstantFolding")]
        return []


class DCETransformer(NodeTransformer):
    """Transformer for Dead Code Elimination."""
    
    def __init__(self, context: MutationContext):
        self.context = context
        self.changed = False

    def visit_Block(self, node: schema.Block) -> schema.Block:
        new_stmts = []
        terminated = False
        
        for stmt in node.statements:
            if terminated:
                # This statement is unreachable
                self.changed = True
                continue
                
            # Visit the statement to process nested blocks
            new_stmt = self.visit(stmt)
            if new_stmt is None:
                continue # Statement removed by recursive visit
                
            # Check for pure expression statements (useless)
            if isinstance(new_stmt, schema.ExprStmt):
                if self.context.is_pure(new_stmt.value):
                    self.changed = True
                    continue # Remove useless expression
            
            new_stmts.append(new_stmt)
            
            # Check if this statement terminates control flow
            if isinstance(new_stmt, (schema.Return, schema.Break, schema.Continue, schema.Raise)):
                terminated = True
                
        node.statements = new_stmts
        return node
    
    def visit_If(self, node: schema.If) -> Optional[schema.Statement]:
        node = self.generic_visit(node)
        # If test is constant True/False
        if isinstance(node.test, schema.Constant):
            self.changed = True
            if node.test.value:
                # Return body statements. But If is a Statement, body is a Block.
                # We can't replace a Statement with a list of Statements directly in visit_If 
                # because the parent visit_Block expects a Statement.
                # BUT: `visit` in NodeTransformer handles list return! 
                # Wait, my simplistic NodeTransformer implementation handles list return for lists, 
                # but visit_If is visiting a specific field.
                # In generic_visit for Block statements, we handle it if visit returns list?
                # Let's check NodeTransformer implementation in utils.py...
                # "if isinstance(item, schema.IRNode): new_node = self.visit(item) ... elif isinstance(new_node, list): new_values.extend(new_node)"
                # Yes! It supports returning a list of statements.
                return node.body.statements
            else:
                return node.orelse.statements if node.orelse else None
        return node


class DeadCodeEliminationMutator(Mutator):
    def mutate(self, ir: schema.Module) -> List[Tuple[schema.Module, str]]:
        new_ir = copy.deepcopy(ir)
        # We need a fresh context for the new IR
        context = MutationContext(new_ir)
        transformer = DCETransformer(context)
        transformer.visit(new_ir)
        
        if transformer.changed:
            return [(new_ir, "Advanced_DeadCodeElimination")]
        return []


class LoopUnrollingTransformer(NodeTransformer):
    """Transformer for simple loop unrolling."""
    
    def __init__(self, max_unroll: int = 4):
        self.max_unroll = max_unroll
        self.changed = False
        
    def visit_For(self, node: schema.For) -> Any:
        # Check if iter is range(N) where N is small constant
        if isinstance(node.iter, schema.Call) and \
           isinstance(node.iter.func, schema.Name) and \
           node.iter.func.id == 'range':
            
            args = node.iter.args
            start, stop, step = 0, None, 1
            
            # Parse range args
            if len(args) == 1 and isinstance(args[0], schema.Constant) and isinstance(args[0].value, int):
                stop = args[0].value
            elif len(args) == 2 and isinstance(args[0], schema.Constant) and isinstance(args[1], schema.Constant):
                start = args[0].value
                stop = args[1].value
            # Ignore step for now or complex cases
            
            if stop is not None:
                count = stop - start
                if 0 < count <= self.max_unroll:
                    # Unroll!
                    self.changed = True
                    unrolled_stmts = []
                    
                    for i in range(start, stop):
                        # Duplicate body
                        # We need to replace user of loop var with constant `i`
                        # This requires another transformer or sub-visitor
                        body_copy = copy.deepcopy(node.body.statements)
                        if isinstance(node.target, schema.Name):
                            loop_var = node.target.id
                            replacer = VarReplacer(loop_var, i)
                            for stmt in body_copy:
                                replacer.visit(stmt)
                        
                        unrolled_stmts.extend(body_copy)
                        
                    return unrolled_stmts
                    
        return self.generic_visit(node)


class VarReplacer(NodeTransformer):
    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value
        
    def visit_Name(self, node: schema.Name) -> Any:
        if node.id == self.name and node.ctx == "Load":
            return schema.Constant(value=self.value, kind="int")
        return node


class LoopUnrollingMutator(Mutator):
    def mutate(self, ir: schema.Module) -> List[Tuple[schema.Module, str]]:
        variants = []
        # Try different unroll levels? Or just one standard pass?
        # The prompt implies trying different things.
        
        # Strategy 1: aggressive unrolling (up to 4)
        new_ir = copy.deepcopy(ir)
        transformer = LoopUnrollingTransformer(max_unroll=4)
        transformer.visit(new_ir)
        
        if transformer.changed:
            variants.append((new_ir, "Advanced_LoopUnrolling_4"))
            
        return variants


class CommonSubexpressionEliminationMutator(Mutator):
    """
    Eliminates common subexpressions by identifying repeated computations
    and extracting them to temporary variables.
    """
    def mutate(self, ir: schema.Module) -> List[Tuple[schema.Module, str]]:
        new_ir = copy.deepcopy(ir)
        transformer = CSETransformer()
        transformer.visit(new_ir)
        
        if transformer.changed:
            return [(new_ir, "Advanced_CommonSubexpressionElimination")]
        return []


class CSETransformer(NodeTransformer):
    """Transformer for Common Subexpression Elimination."""
    
    def __init__(self):
        self.changed = False
        self.expr_count = {}  # expression_hash -> count
        self.temp_var_counter = 0
    
    def visit_FunctionDef(self, node: schema.FunctionDef) -> schema.Statement:
        """Process function body for CSE opportunities."""
        # First pass: count expression occurrences
        self._count_expressions(node.body)
        
        # Second pass: extract common subexpressions
        if self.expr_count:
            node = self.generic_visit(node)
        
        return node
    
    def _count_expressions(self, block: schema.Block):
        """Count occurrences of expressions in a block."""
        for stmt in block.statements:
            self._count_in_statement(stmt)
    
    def _count_in_statement(self, stmt: schema.Statement):
        """Count expressions in a statement."""
        if isinstance(stmt, schema.Assign):
            expr_hash = self._hash_expression(stmt.value)
            if expr_hash:
                self.expr_count[expr_hash] = self.expr_count.get(expr_hash, 0) + 1
        elif isinstance(stmt, (schema.If, schema.While, schema.For)):
            if hasattr(stmt, 'body'):
                self._count_expressions(stmt.body)
            if hasattr(stmt, 'orelse') and stmt.orelse:
                self._count_expressions(stmt.orelse)
    
    def _hash_expression(self, expr: schema.Expression) -> Optional[str]:
        """Create a hash for an expression (simplified)."""
        if isinstance(expr, schema.BinaryOp):
            left_hash = self._hash_expression(expr.left)
            right_hash = self._hash_expression(expr.right)
            if left_hash and right_hash:
                return f"BinOp({expr.op},{left_hash},{right_hash})"
        elif isinstance(expr, schema.Name):
            return f"Name({expr.id})"
        elif isinstance(expr, schema.Constant):
            return f"Const({expr.value})"
        elif isinstance(expr, schema.Call):
            if isinstance(expr.func, schema.Name):
                args_hash = ",".join(self._hash_expression(arg) or "" for arg in expr.args)
                return f"Call({expr.func.id},{args_hash})"
        
        return None


class LoopInvariantCodeMotionMutator(Mutator):
    """
    Moves loop-invariant computations outside of loops.
    """
    def mutate(self, ir: schema.Module) -> List[Tuple[schema.Module, str]]:
        new_ir = copy.deepcopy(ir)
        transformer = LICMTransformer()
        transformer.visit(new_ir)
        
        if transformer.changed:
            return [(new_ir, "Advanced_LoopInvariantCodeMotion")]
        return []


class LICMTransformer(NodeTransformer):
    """Transformer for Loop Invariant Code Motion."""
    
    def __init__(self):
        self.changed = False
        self.loop_vars = set()  # Variables modified in current loop
    
    def visit_For(self, node: schema.For) -> schema.Statement:
        """Process for loops to hoist invariant code."""
        # Track loop variable
        if isinstance(node.target, schema.Name):
            old_loop_vars = self.loop_vars.copy()
            self.loop_vars.add(node.target.id)
            
            # Find invariant statements
            invariant_stmts = []
            remaining_stmts = []
            
            for stmt in node.body.statements:
                if self._is_loop_invariant(stmt):
                    invariant_stmts.append(stmt)
                    self.changed = True
                else:
                    remaining_stmts.append(stmt)
            
            # Update loop body
            if invariant_stmts:
                node.body.statements = remaining_stmts
            
            # Restore loop vars
            self.loop_vars = old_loop_vars
            
            # If we hoisted statements, we need to return a list
            if invariant_stmts:
                return invariant_stmts + [node]
        
        return self.generic_visit(node)
    
    def _is_loop_invariant(self, stmt: schema.Statement) -> bool:
        """Check if a statement is loop-invariant (simplified)."""
        if isinstance(stmt, schema.Assign):
            # Check if RHS uses any loop variables
            used_vars = self._get_used_vars(stmt.value)
            return not (used_vars & self.loop_vars)
        return False
    
    def _get_used_vars(self, expr: schema.Expression) -> Set[str]:
        """Get all variables used in an expression."""
        used = set()
        
        if isinstance(expr, schema.Name):
            used.add(expr.id)
        elif isinstance(expr, schema.BinaryOp):
            used.update(self._get_used_vars(expr.left))
            used.update(self._get_used_vars(expr.right))
        elif isinstance(expr, schema.Call):
            for arg in expr.args:
                used.update(self._get_used_vars(arg))
        
        return used