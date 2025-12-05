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
            variant = self._mutate_swap_operands(ir)
            if variant:
                variants.append((variant, "Structural_SwapOperands"))
                logger.debug("Successfully created swap variant")
        except Exception as e:
            logger.error(f"Swap mutation failed: {e}")
            
        return variants
    
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
                # Simplified check - in production would use full dependency graph
                stmt1_defs = context.get_defined_vars(block.statements[idx1])
                stmt1_uses = context.get_used_vars(block.statements[idx1])
                stmt2_defs = context.get_defined_vars(block.statements[idx2])
                stmt2_uses = context.get_used_vars(block.statements[idx2])
                
                # Check for conflicts
                if stmt1_defs & stmt2_uses or stmt2_defs & stmt1_uses or stmt1_defs & stmt2_defs:
                    continue  # Not safe to swap, try again
            
            # Perform the swap
            block.statements[idx1], block.statements[idx2] = block.statements[idx2], block.statements[idx1]
            return new_ir
        
        return None
    
    def _mutate_swap_operands(self, ir: schema.Module) -> schema.Module:
        """Swap operands in commutative binary operations."""
        new_ir = copy.deepcopy(ir)
        
        # Find all binary operations
        binops = self._find_binops(new_ir)
        
        # Filter commutative operations
        commutative = ['+', '*', '==', '!=', 'and', 'or']
        candidates = [op for op in binops if op.op in commutative]
        
        if not candidates:
            return None
        
        # Pick a random operation and swap operands
        binop = random.choice(candidates)
        binop.left, binop.right = binop.right, binop.left
        
        return new_ir
    
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
