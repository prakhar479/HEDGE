"""
Structural Mutators - IR-based program transformations.

These mutators operate strictly on the IR tree and perform
semantics-preserving transformations.
"""
import random
import copy
import logging
from typing import List, Tuple
from src.domain.interfaces import Mutator
from src.domain.ir import schema
from src.domain.ir.context import MutationContext
from src.domain.ir.utils import NodeTransformer
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

class StructuralMutator(Mutator):
    """
    Performs structural mutations on the IR tree.
    
    These are syntax-preserving transformations that don't change
    the program's semantics, only its structure.
    
    Strategies:
    1. Reorder independent statements
    2. Swap commutative operands
    3. Rename variables consistently
    """
    
    def __init__(self, use_context: bool = True):
        """
        Args:
            use_context: If True, uses MutationContext for safe transformations
        """
        self.use_context = use_context
    
    def mutate(self, ir: schema.Module) -> List[Tuple[schema.Module, str]]:
        """
        Apply structural mutations to the IR.
        
        Args:
            ir: The input IR module
            
        Returns:
            List of (mutated_ir, strategy_name) tuples
        """
        variants = []
        
        # Build context if enabled
        context = None
        if self.use_context:
            try:
                context = MutationContext(ir)
                logger.debug(f"Built mutation context with {len(context.symbol_table)} symbols")
            except Exception as e:
                logger.warning(f"Failed to build context: {e}. Proceeding without context.")
        
        # Strategy 1: Reorder independent statements
        try:
            variant = self._mutate_reorder(ir, context)
            if variant:
                variants.append((variant, "Structural_ReorderStatements"))
                logger.debug("Successfully created reorder variant")
        except Exception as e:
            logger.error(f"Reorder mutation failed: {e}")
        
        # Strategy 2: Swap binary operands (commutative ops)
        try:
            variant = self._mutate_swap_operands(ir, context)
            if variant:
                variants.append((variant, "Structural_SwapOperands"))
                logger.debug("Successfully created swap variant")
        except Exception as e:
            logger.error(f"Swap mutation failed: {e}")

        # Strategy 3: Augmented Assignment
        try:
            variant = self._mutate_aug_assign(ir)
            if variant:
                variants.append((variant, "Structural_AugAssign"))
        except Exception as e:
            logger.error(f"AugAssign mutation failed: {e}")

        # Strategy 5: Strength Reduction
        try:
            variant = self._mutate_strength_reduction(ir)
            if variant:
                variants.append((variant, "Structural_StrengthReduction"))
        except Exception as e:
            logger.error(f"StrengthReduction mutation failed: {e}")

        # Strategy 6: Fast Membership (List -> Set)
        try:
            variant = self._mutate_fast_membership(ir)
            if variant:
                variants.append((variant, "Structural_FastMembership"))
        except Exception as e:
            logger.error(f"FastMembership mutation failed: {e}")

        # Strategy 7: Algebraic Simplification
        try:
            variant = self._mutate_algebraic_simplification(ir)
            if variant:
                variants.append((variant, "Structural_AlgebraicSimplification"))
        except Exception as e:
            logger.error(f"AlgebraicSimplification mutation failed: {e}")

        # Strategy 8: Loop Optimization
        try:
            variant = self._mutate_loop_optimization(ir)
            if variant:
                variants.append((variant, "Structural_LoopOptimization"))
        except Exception as e:
            logger.error(f"LoopOptimization mutation failed: {e}")
            
        return variants

    def _mutate_strength_reduction(self, ir: schema.Module) -> Optional[schema.Module]:
        """Replace expensive operations with cheaper ones (e.g. x**2 -> x*x)."""
        new_ir = copy.deepcopy(ir)
        transformer = StrengthReductionTransformer()
        transformer.visit(new_ir)
        return new_ir if transformer.changed else None

    def _mutate_fast_membership(self, ir: schema.Module) -> Optional[schema.Module]:
        """Replace x in [a,b] with x in {a,b} for constant lists."""
        new_ir = copy.deepcopy(ir)
        transformer = FastMembershipTransformer()
        transformer.visit(new_ir)
        return new_ir if transformer.changed else None

    def _mutate_algebraic_simplification(self, ir: schema.Module) -> Optional[schema.Module]:
        """Apply algebraic simplifications and boolean algebra."""
        new_ir = copy.deepcopy(ir)
        transformer = AlgebraicSimplificationTransformer()
        transformer.visit(new_ir)
        return new_ir if transformer.changed else None

    def _mutate_loop_optimization(self, ir: schema.Module) -> Optional[schema.Module]:
        """Apply loop optimizations like fusion and peeling."""
        new_ir = copy.deepcopy(ir)
        transformer = LoopOptimizationTransformer()
        transformer.visit(new_ir)
        return new_ir if transformer.changed else None

    
    def _mutate_reorder(self, ir: schema.Module, context=None) -> schema.Module:
        """
        Reorder consecutive independent statements.
        
        Uses dependency analysis if context is provided to ensure
        the reordering is semantics-preserving.
        
        Args:
            ir: The IR module
            context: Optional MutationContext for dependency analysis
            
        Returns:
            Mutated IR or None if no safe reordering is possible
        """
        new_ir = copy.deepcopy(ir)
        
        # Find all blocks in the IR
        blocks = self._find_blocks(new_ir)
        
        # Filter blocks with at least 2 statements
        candidates = [blk for blk in blocks if len(blk.statements) >= 2]
        
        if not candidates:
            return None
        
        # Try multiple times to find a valid swap
        max_attempts = 10
        for _ in range(max_attempts):
            # Pick a random block and two statements
            block = random.choice(candidates)
            if len(block.statements) < 2:
                continue
            
            idx1, idx2 = random.sample(range(len(block.statements)), 2)
            
            # If we have context, check if swap is safe
            if context:
                stmt1 = block.statements[idx1]
                stmt2 = block.statements[idx2]
                
                # Check 1: Purity (avoid reordering side effects)
                if not context.is_pure(stmt1) or not context.is_pure(stmt2):
                    continue

                # Check 2: Data Dependencies
                stmt1_defs = context.get_defined_vars(stmt1)
                stmt1_uses = context.get_used_vars(stmt1)
                stmt2_defs = context.get_defined_vars(stmt2)
                stmt2_uses = context.get_used_vars(stmt2)
                
                # Check for conflicts
                if stmt1_defs & stmt2_uses or stmt2_defs & stmt1_uses or stmt1_defs & stmt2_defs:
                    continue  # Not safe to swap, try again
            
            # Perform the swap
            block.statements[idx1], block.statements[idx2] = block.statements[idx2], block.statements[idx1]
            return new_ir
        
        return None
    
    def _mutate_swap_operands(self, ir: schema.Module, context=None) -> schema.Module:
        """Swap operands in commutative binary operations."""
        new_ir = copy.deepcopy(ir)
        
        # Build local context if not provided (though usually it is)
        if not context and self.use_context:
            try:
                context = MutationContext(new_ir)
            except:
                 pass

        # Find all binary operations
        binops = self._find_binops(new_ir)
        
        # Filter commutative operations
        commutative = ['+', '*', '==', '!=', 'and', 'or', '^', '&', '|']
        candidates = []
        for op in binops:
            if op.op in commutative:
                # Safety check: Operands must be pure
                if context:
                    if not context.is_pure(op.left) or not context.is_pure(op.right):
                        continue
                candidates.append(op)
        
        if not candidates:
            return None
        
        # Pick a random operation and swap operands
        binop = random.choice(candidates)
        binop.left, binop.right = binop.right, binop.left
        
        return new_ir

    def _mutate_aug_assign(self, ir: schema.Module) -> schema.Module:
        """Replace x = x + y with x += y."""
        new_ir = copy.deepcopy(ir)
        blocks = self._find_blocks(new_ir)
        
        candidates = []
        for block in blocks:
            for i, stmt in enumerate(block.statements):
                if isinstance(stmt, schema.Assign) and len(stmt.targets) == 1:
                    target = stmt.targets[0]
                    if isinstance(target, schema.Name) and isinstance(stmt.value, schema.BinaryOp):
                        # Check if target is used in binary op
                        # x = x + y or x = y + x
                        if isinstance(stmt.value.left, schema.Name) and stmt.value.left.id == target.id:
                            candidates.append((block, i, stmt, stmt.value.op, stmt.value.right))
                        elif isinstance(stmt.value.right, schema.Name) and stmt.value.right.id == target.id and stmt.value.op in ['+', '*']:
                            candidates.append((block, i, stmt, stmt.value.op, stmt.value.left))
                            
        if not candidates:
            return None
            
        block, idx, stmt, op, value = random.choice(candidates)
        block.statements[idx] = schema.AugAssign(
            target=stmt.targets[0],
            op=op,
            value=value
        )
        return new_ir

    def _mutate_range(self, ir: schema.Module) -> schema.Module:
        """Replace range(0, n) with range(n)."""
        new_ir = copy.deepcopy(ir)
        calls = self._find_calls(new_ir)
        
        candidates = []
        for call in calls:
            if isinstance(call.func, schema.Name) and call.func.id == 'range' and len(call.args) == 2:
                if isinstance(call.args[0], schema.Constant) and call.args[0].value == 0:
                    candidates.append(call)
                    
        if not candidates:
            return None
            
        call = random.choice(candidates)
        call.args = [call.args[1]]
        return new_ir

    def _find_calls(self, node) -> List[schema.Call]:
        """Recursively find all Call nodes."""
        calls = []
        if isinstance(node, schema.Call):
            calls.append(node)
            
        if hasattr(node, '__dict__'):
            for key, value in node.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, '__dict__'):
                            calls.extend(self._find_calls(item))
                elif hasattr(value, '__dict__'):
                    calls.extend(self._find_calls(value))
        return calls
    
    def _find_blocks(self, node) -> List[schema.Block]:
        """Recursively find all Block nodes in the IR tree."""
        blocks = []
        
        if isinstance(node, schema.Block):
            blocks.append(node)
            for stmt in node.statements:
                blocks.extend(self._find_blocks(stmt))
        elif isinstance(node, schema.FunctionDef):
            blocks.extend(self._find_blocks(node.body))
        elif isinstance(node, (schema.If, schema.While, schema.For)):
            blocks.extend(self._find_blocks(node.body))
            if hasattr(node, 'orelse') and node.orelse:
                blocks.extend(self._find_blocks(node.orelse))
        elif isinstance(node, schema.Module):
            blocks.extend(self._find_blocks(node.body))
        
        return blocks
    
    def _find_binops(self, node) -> List[schema.BinaryOp]:
        """Recursively find all BinaryOp nodes in the IR tree."""
        binops = []
        
        if isinstance(node, schema.BinaryOp):
            binops.append(node)
            binops.extend(self._find_binops(node.left))
            binops.extend(self._find_binops(node.right))
        elif isinstance(node, schema.UnaryOp):
            binops.extend(self._find_binops(node.operand))
        elif isinstance(node, schema.Call):
            for arg in node.args:
                binops.extend(self._find_binops(arg))
        elif isinstance(node, schema.Assign):
            binops.extend(self._find_binops(node.value))
        elif isinstance(node, schema.AugAssign):
            binops.extend(self._find_binops(node.value))
            binops.extend(self._find_binops(node.target))
        elif isinstance(node, schema.Return):
            if node.value:
                binops.extend(self._find_binops(node.value))
        elif isinstance(node, schema.If):
            binops.extend(self._find_binops(node.test))
            binops.extend(self._find_binops(node.body))
            if node.orelse:
                binops.extend(self._find_binops(node.orelse))
        elif isinstance(node, schema.While):
            binops.extend(self._find_binops(node.test))
            binops.extend(self._find_binops(node.body))
        elif isinstance(node, schema.For):
            binops.extend(self._find_binops(node.iter))
            binops.extend(self._find_binops(node.body))
        elif isinstance(node, schema.Block):
            for stmt in node.statements:
                binops.extend(self._find_binops(stmt))
        elif isinstance(node, schema.FunctionDef):
            binops.extend(self._find_binops(node.body))
        elif isinstance(node, schema.Module):
            binops.extend(self._find_binops(node.body))
        
        return binops
        

class StrengthReductionTransformer(NodeTransformer):
    """
    Performs strength reduction: replacing expensive operations with cheaper ones.
    """
    def __init__(self):
        self.changed = False

    def visit_BinaryOp(self, node: schema.BinaryOp) -> schema.Expression:
        node = self.generic_visit(node)
        
        # Power optimizations
        if node.op == '**' and isinstance(node.right, schema.Constant):
            if node.right.value == 2:
                # x ** 2 -> x * x
                self.changed = True
                return schema.BinaryOp(left=node.left, op='*', right=node.left)
            elif node.right.value == 3:
                # x ** 3 -> x * x * x
                self.changed = True
                x_squared = schema.BinaryOp(left=node.left, op='*', right=node.left)
                return schema.BinaryOp(left=x_squared, op='*', right=node.left)
            elif node.right.value == 0.5:
                # x ** 0.5 -> math.sqrt(x)
                self.changed = True
                return schema.Call(
                    func=schema.Attribute(value=schema.Name(id='math'), attr='sqrt'),
                    args=[node.left]
                )
        
        # Division optimizations
        if node.op == '/' and isinstance(node.right, schema.Constant):
            if node.right.value == 2:
                # x / 2 -> x * 0.5
                self.changed = True
                return schema.BinaryOp(
                    left=node.left, op='*', 
                    right=schema.Constant(value=0.5, kind="float")
                )
        
        # Multiplication optimizations
        if node.op == '*':
            if isinstance(node.right, schema.Constant):
                if node.right.value == 0:
                    # x * 0 -> 0
                    self.changed = True
                    return schema.Constant(value=0, kind="int")
                elif node.right.value == 1:
                    # x * 1 -> x
                    self.changed = True
                    return node.left
            elif isinstance(node.left, schema.Constant):
                if node.left.value == 0:
                    # 0 * x -> 0
                    self.changed = True
                    return schema.Constant(value=0, kind="int")
                elif node.left.value == 1:
                    # 1 * x -> x
                    self.changed = True
                    return node.right
        
        # Addition optimizations
        if node.op == '+':
            if isinstance(node.right, schema.Constant) and node.right.value == 0:
                # x + 0 -> x
                self.changed = True
                return node.left
            elif isinstance(node.left, schema.Constant) and node.left.value == 0:
                # 0 + x -> x
                self.changed = True
                return node.right
        
        # Subtraction optimizations
        if node.op == '-':
            if isinstance(node.right, schema.Constant) and node.right.value == 0:
                # x - 0 -> x
                self.changed = True
                return node.left
        
        # Floor division optimizations
        if node.op == '//' and isinstance(node.right, schema.Constant) and node.right.value == 1:
            # x // 1 -> x
            self.changed = True
            return node.left
        
        # Modulo optimizations
        if node.op == '%' and isinstance(node.right, schema.Constant) and node.right.value == 1:
            # x % 1 -> 0
            self.changed = True
            return schema.Constant(value=0, kind="int")
            
        return node
    
    def visit_If(self, node: schema.If) -> schema.Statement:
        node = self.generic_visit(node)
        
        # len(seq) > 0 -> seq
        if isinstance(node.test, schema.Compare) and len(node.test.ops) == 1:
            op = node.test.ops[0]
            left = node.test.left
            right = node.test.comparators[0]
            
            # Check for len(x) > 0
            if op == '>' and isinstance(right, schema.Constant) and right.value == 0:
                if isinstance(left, schema.Call) and isinstance(left.func, schema.Name) and left.func.id == 'len':
                    if len(left.args) == 1:
                        self.changed = True
                        node.test = left.args[0]
                        
        return node

class FastMembershipTransformer(NodeTransformer):
    """
    Optimizes membership tests.
    x in [a, b] -> x in {a, b} (O(N) -> O(1))
    """
    def __init__(self):
        self.changed = False
        
    def visit_Compare(self, node: schema.Compare) -> schema.Expression:
        node = self.generic_visit(node)
        
        if len(node.ops) != 1 or len(node.comparators) != 1:
            return node
            
        op = node.ops[0]
        comparator = node.comparators[0]
        
        if op in ('in', 'not in') and isinstance(comparator, schema.ListExpr):
            # Convert ListExpr to SetExpr
            # Only if all elements are hashable constants
            # For safety, let's just check if they are Constants
            all_const = all(isinstance(elt, schema.Constant) for elt in comparator.elts)
            
            if all_const:
                self.changed = True
                node.comparators[0] = schema.SetExpr(elts=comparator.elts)
                
        return node


class AlgebraicSimplificationTransformer(NodeTransformer):
    """
    Performs algebraic simplifications and boolean algebra optimizations.
    """
    def __init__(self):
        self.changed = False
    
    def visit_UnaryOp(self, node: schema.UnaryOp) -> schema.Expression:
        node = self.generic_visit(node)
        
        # Double negation: not not x -> x
        if node.op == 'not' and isinstance(node.operand, schema.UnaryOp) and node.operand.op == 'not':
            self.changed = True
            return node.operand.operand
        
        # De Morgan's laws: not (a and b) -> (not a) or (not b)
        if node.op == 'not' and isinstance(node.operand, schema.BoolOp):
            if node.operand.op == 'and':
                self.changed = True
                negated_values = [schema.UnaryOp(op='not', operand=val) for val in node.operand.values]
                return schema.BoolOp(op='or', values=negated_values)
            elif node.operand.op == 'or':
                self.changed = True
                negated_values = [schema.UnaryOp(op='not', operand=val) for val in node.operand.values]
                return schema.BoolOp(op='and', values=negated_values)
        
        return node
    
    def visit_BoolOp(self, node: schema.BoolOp) -> schema.Expression:
        node = self.generic_visit(node)
        
        # Short-circuit optimizations
        if node.op == 'and':
            # Remove True values: True and x -> x
            filtered_values = []
            for val in node.values:
                if isinstance(val, schema.Constant) and val.value is True:
                    continue  # Skip True values
                elif isinstance(val, schema.Constant) and val.value is False:
                    # False and anything -> False
                    self.changed = True
                    return schema.Constant(value=False, kind="bool")
                else:
                    filtered_values.append(val)
            
            if len(filtered_values) != len(node.values):
                self.changed = True
                if len(filtered_values) == 0:
                    return schema.Constant(value=True, kind="bool")
                elif len(filtered_values) == 1:
                    return filtered_values[0]
                else:
                    node.values = filtered_values
        
        elif node.op == 'or':
            # Remove False values: False or x -> x
            filtered_values = []
            for val in node.values:
                if isinstance(val, schema.Constant) and val.value is False:
                    continue  # Skip False values
                elif isinstance(val, schema.Constant) and val.value is True:
                    # True or anything -> True
                    self.changed = True
                    return schema.Constant(value=True, kind="bool")
                else:
                    filtered_values.append(val)
            
            if len(filtered_values) != len(node.values):
                self.changed = True
                if len(filtered_values) == 0:
                    return schema.Constant(value=False, kind="bool")
                elif len(filtered_values) == 1:
                    return filtered_values[0]
                else:
                    node.values = filtered_values
        
        return node
    
    def visit_Compare(self, node: schema.Compare) -> schema.Expression:
        node = self.generic_visit(node)
        
        # Comparison chain optimizations
        if len(node.ops) == 1 and len(node.comparators) == 1:
            op = node.ops[0]
            left = node.left
            right = node.comparators[0]
            
            # x == x -> True
            if op == '==' and self._nodes_equal(left, right):
                self.changed = True
                return schema.Constant(value=True, kind="bool")
            
            # x != x -> False
            if op == '!=' and self._nodes_equal(left, right):
                self.changed = True
                return schema.Constant(value=False, kind="bool")
            
            # x < x, x > x -> False
            if op in ('<', '>') and self._nodes_equal(left, right):
                self.changed = True
                return schema.Constant(value=False, kind="bool")
            
            # x <= x, x >= x -> True
            if op in ('<=', '>=') and self._nodes_equal(left, right):
                self.changed = True
                return schema.Constant(value=True, kind="bool")
        
        return node
    
    def _nodes_equal(self, node1: schema.Expression, node2: schema.Expression) -> bool:
        """Check if two nodes are structurally equal (simplified check)."""
        if type(node1) != type(node2):
            return False
        
        if isinstance(node1, schema.Name):
            return node1.id == node2.id
        elif isinstance(node1, schema.Constant):
            return node1.value == node2.value
        
        # For more complex nodes, we'd need deeper comparison
        return False


class LoopOptimizationTransformer(NodeTransformer):
    """
    Performs loop optimizations including fusion and peeling.
    """
    def __init__(self):
        self.changed = False
    
    def visit_Block(self, node: schema.Block) -> schema.Block:
        node = self.generic_visit(node)
        
        # Look for adjacent loops that can be fused
        new_statements = []
        i = 0
        while i < len(node.statements):
            stmt = node.statements[i]
            
            if isinstance(stmt, schema.For) and i + 1 < len(node.statements):
                next_stmt = node.statements[i + 1]
                if isinstance(next_stmt, schema.For):
                    # Check if loops can be fused
                    if self._can_fuse_loops(stmt, next_stmt):
                        fused_loop = self._fuse_loops(stmt, next_stmt)
                        new_statements.append(fused_loop)
                        self.changed = True
                        i += 2  # Skip both loops
                        continue
            
            new_statements.append(stmt)
            i += 1
        
        node.statements = new_statements
        return node
    
    def _can_fuse_loops(self, loop1: schema.For, loop2: schema.For) -> bool:
        """Check if two loops can be safely fused."""
        # Simplified check: same iteration variable and range
        if not (isinstance(loop1.target, schema.Name) and isinstance(loop2.target, schema.Name)):
            return False
        
        if loop1.target.id != loop2.target.id:
            return False
        
        # Check if iteration spaces are the same (simplified)
        return self._ranges_equal(loop1.iter, loop2.iter)
    
    def _ranges_equal(self, iter1: schema.Expression, iter2: schema.Expression) -> bool:
        """Check if two iteration expressions are equal (simplified)."""
        if type(iter1) != type(iter2):
            return False
        
        if isinstance(iter1, schema.Call) and isinstance(iter2, schema.Call):
            if (isinstance(iter1.func, schema.Name) and isinstance(iter2.func, schema.Name) and
                iter1.func.id == iter2.func.id == 'range'):
                # Compare range arguments
                if len(iter1.args) == len(iter2.args):
                    return all(self._expressions_equal(a1, a2) for a1, a2 in zip(iter1.args, iter2.args))
        
        return False
    
    def _expressions_equal(self, expr1: schema.Expression, expr2: schema.Expression) -> bool:
        """Check if two expressions are equal (simplified)."""
        if type(expr1) != type(expr2):
            return False
        
        if isinstance(expr1, schema.Constant):
            return expr1.value == expr2.value
        elif isinstance(expr1, schema.Name):
            return expr1.id == expr2.id
        
        return False
    
    def _fuse_loops(self, loop1: schema.For, loop2: schema.For) -> schema.For:
        """Fuse two compatible loops."""
        # Combine loop bodies
        combined_body = schema.Block(
            statements=loop1.body.statements + loop2.body.statements
        )
        
        return schema.For(
            target=loop1.target,
            iter=loop1.iter,
            body=combined_body,
            orelse=None  # Simplified: ignore orelse for now
        )

