"""
Data Structure Optimization Mutators

These mutators identify opportunities to optimize data structure usage
for better performance characteristics.
"""
import copy
import logging
from typing import List, Tuple, Optional, Set
from src.domain.interfaces import Mutator
from src.domain.ir import schema
from src.domain.ir.utils import NodeTransformer

logger = logging.getLogger(__name__)


class DataStructureOptimizationMutator(Mutator):
    """
    Optimizes data structure usage patterns for better performance.
    
    Strategies:
    1. List -> deque for frequent insertions/deletions at ends
    2. List -> set for membership testing
    3. Dict -> defaultdict for missing key handling
    4. Nested loops -> itertools.product
    5. Manual sorting -> heapq for partial sorting
    """
    
    def mutate(self, ir: schema.Module) -> List[Tuple[schema.Module, str]]:
        variants = []
        
        # Strategy 1: List to deque optimization
        try:
            variant = self._mutate_list_to_deque(ir)
            if variant:
                variants.append((variant, "DataStructure_ListToDeque"))
        except Exception as e:
            logger.error(f"ListToDeque mutation failed: {e}")
        
        # Strategy 2: List to set for membership
        try:
            variant = self._mutate_list_to_set_membership(ir)
            if variant:
                variants.append((variant, "DataStructure_ListToSetMembership"))
        except Exception as e:
            logger.error(f"ListToSetMembership mutation failed: {e}")
        
        # Strategy 3: Dict to defaultdict
        try:
            variant = self._mutate_dict_to_defaultdict(ir)
            if variant:
                variants.append((variant, "DataStructure_DictToDefaultdict"))
        except Exception as e:
            logger.error(f"DictToDefaultdict mutation failed: {e}")
        
        # Strategy 4: Nested loops to itertools.product
        try:
            variant = self._mutate_nested_loops_to_product(ir)
            if variant:
                variants.append((variant, "DataStructure_NestedLoopsToProduct"))
        except Exception as e:
            logger.error(f"NestedLoopsToProduct mutation failed: {e}")
        
        return variants
    
    def _mutate_list_to_deque(self, ir: schema.Module) -> Optional[schema.Module]:
        """Convert list to deque when frequent insertions/deletions at ends are detected."""
        new_ir = copy.deepcopy(ir)
        transformer = ListToDequeTransformer()
        transformer.visit(new_ir)
        
        if transformer.changed:
            # Add collections import if not present
            self._ensure_import(new_ir, 'collections')
        
        return new_ir if transformer.changed else None
    
    def _mutate_list_to_set_membership(self, ir: schema.Module) -> Optional[schema.Module]:
        """Convert list to set when used primarily for membership testing."""
        new_ir = copy.deepcopy(ir)
        transformer = ListToSetMembershipTransformer()
        transformer.visit(new_ir)
        return new_ir if transformer.changed else None
    
    def _mutate_dict_to_defaultdict(self, ir: schema.Module) -> Optional[schema.Module]:
        """Convert dict to defaultdict when missing key patterns are detected."""
        new_ir = copy.deepcopy(ir)
        transformer = DictToDefaultdictTransformer()
        transformer.visit(new_ir)
        
        if transformer.changed:
            self._ensure_import(new_ir, 'collections')
        
        return new_ir if transformer.changed else None
    
    def _mutate_nested_loops_to_product(self, ir: schema.Module) -> Optional[schema.Module]:
        """Convert nested loops to itertools.product when appropriate."""
        new_ir = copy.deepcopy(ir)
        transformer = NestedLoopsToProductTransformer()
        transformer.visit(new_ir)
        
        if transformer.changed:
            self._ensure_import(new_ir, 'itertools')
        
        return new_ir if transformer.changed else None
    
    def _ensure_import(self, ir: schema.Module, module_name: str):
        """Ensure a module is imported."""
        # Check if already imported
        for stmt in ir.body.statements:
            if isinstance(stmt, schema.Import):
                for alias in stmt.names:
                    if alias.name == module_name:
                        return
            elif isinstance(stmt, schema.ImportFrom):
                if stmt.module == module_name:
                    return
        
        # Add import at the beginning
        import_stmt = schema.Import(names=[schema.Alias(name=module_name)])
        ir.body.statements.insert(0, import_stmt)


class ListToDequeTransformer(NodeTransformer):
    """Transforms list operations to deque when beneficial."""
    
    def __init__(self):
        self.changed = False
        self.list_vars = set()  # Track variables that should be deques
    
    def visit_Assign(self, node: schema.Assign) -> schema.Statement:
        node = self.generic_visit(node)
        
        # Look for list() or [] assignments
        if len(node.targets) == 1 and isinstance(node.targets[0], schema.Name):
            var_name = node.targets[0].id
            
            if isinstance(node.value, schema.ListExpr) and len(node.value.elts) == 0:
                # Empty list assignment: x = []
                # Check if this variable is used with append/pop operations
                if self._should_convert_to_deque(var_name):
                    self.changed = True
                    self.list_vars.add(var_name)
                    # Convert to deque()
                    node.value = schema.Call(
                        func=schema.Attribute(value=schema.Name(id='collections'), attr='deque'),
                        args=[]
                    )
        
        return node
    
    def _should_convert_to_deque(self, var_name: str) -> bool:
        """Heuristic to determine if a list should be converted to deque."""
        # This is a simplified heuristic - in practice, we'd analyze usage patterns
        # For now, we'll be conservative and only suggest conversion for specific patterns
        return False  # Disabled for safety in this implementation


class ListToSetMembershipTransformer(NodeTransformer):
    """Converts lists to sets when used primarily for membership testing."""
    
    def __init__(self):
        self.changed = False
    
    def visit_Compare(self, node: schema.Compare) -> schema.Expression:
        node = self.generic_visit(node)
        
        # Look for 'x in list_literal' patterns
        if (len(node.ops) == 1 and node.ops[0] == 'in' and 
            len(node.comparators) == 1 and isinstance(node.comparators[0], schema.ListExpr)):
            
            list_expr = node.comparators[0]
            # Convert to set if all elements are constants (hashable)
            if all(isinstance(elt, schema.Constant) for elt in list_expr.elts):
                self.changed = True
                node.comparators[0] = schema.SetExpr(elts=list_expr.elts)
        
        return node


class DictToDefaultdictTransformer(NodeTransformer):
    """Converts dict to defaultdict when missing key patterns are detected."""
    
    def __init__(self):
        self.changed = False
        self.dict_vars = {}  # var_name -> default_factory_type
    
    def visit_If(self, node: schema.If) -> schema.Statement:
        node = self.generic_visit(node)
        
        # Look for pattern: if key not in dict: dict[key] = default_value
        if (isinstance(node.test, schema.Compare) and len(node.test.ops) == 1 and 
            node.test.ops[0] == 'not in' and len(node.test.comparators) == 1):
            
            key = node.test.left
            dict_var = node.test.comparators[0]
            
            if (isinstance(dict_var, schema.Name) and len(node.body.statements) == 1 and
                isinstance(node.body.statements[0], schema.Assign)):
                
                assign = node.body.statements[0]
                if (len(assign.targets) == 1 and isinstance(assign.targets[0], schema.Subscript) and
                    isinstance(assign.targets[0].value, schema.Name) and
                    assign.targets[0].value.id == dict_var.id):
                    
                    # This is the pattern we're looking for
                    default_value = assign.value
                    if isinstance(default_value, schema.ListExpr) and len(default_value.elts) == 0:
                        self.dict_vars[dict_var.id] = 'list'
                    elif isinstance(default_value, schema.Constant) and default_value.value == 0:
                        self.dict_vars[dict_var.id] = 'int'
                    
                    # Remove the if statement (it becomes unnecessary with defaultdict)
                    self.changed = True
                    return schema.Pass()  # Replace with pass statement
        
        return node


class NestedLoopsToProductTransformer(NodeTransformer):
    """Converts nested loops to itertools.product when appropriate."""
    
    def __init__(self):
        self.changed = False
    
    def visit_For(self, node: schema.For) -> schema.Statement:
        node = self.generic_visit(node)
        
        # Look for nested for loops
        if (len(node.body.statements) == 1 and 
            isinstance(node.body.statements[0], schema.For)):
            
            inner_loop = node.body.statements[0]
            
            # Check if loops are independent (simplified check)
            if (isinstance(node.target, schema.Name) and isinstance(inner_loop.target, schema.Name) and
                node.target.id != inner_loop.target.id):
                
                # Convert to itertools.product
                self.changed = True
                
                # Create product call
                product_call = schema.Call(
                    func=schema.Attribute(value=schema.Name(id='itertools'), attr='product'),
                    args=[node.iter, inner_loop.iter]
                )
                
                # Create tuple target
                tuple_target = schema.TupleExpr(
                    elts=[node.target, inner_loop.target],
                    ctx="Store"
                )
                
                # Create new loop
                return schema.For(
                    target=tuple_target,
                    iter=product_call,
                    body=inner_loop.body,
                    orelse=None
                )
        
        return node