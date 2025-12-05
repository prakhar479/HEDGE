"""
MutationContext provides metadata and analysis information to mutators.
This enables intelligent, safe mutations that respect program semantics.
"""
from typing import Dict, Set, List, Optional
from dataclasses import dataclass, field
from src.domain.ir.schema import Module, FunctionDef, Name

@dataclass
class SymbolInfo:
    """Information about a symbol in the program."""
    name: str
    type_hint: Optional[str] = None
    is_constant: bool = False
    defined_at: Optional[int] = None  # Line number
    used_at: List[int] = field(default_factory=list)  # Line numbers where used

@dataclass
class ScopeInfo:
    """Information about a lexical scope."""
    scope_type: str  # "module", "function", "class", "block"
    parent: Optional['ScopeInfo'] = None
    symbols: Dict[str, SymbolInfo] = field(default_factory=dict)
    children: List['ScopeInfo'] = field(default_factory=list)

class DependencyGraph:
    """
    Tracks data dependencies between statements.
    Used to determine if mutations are semantics-preserving.
    """
    
    def __init__(self):
        self.dependencies: Dict[int, Set[int]] = {}  # stmt_id -> set of dependent stmt_ids
        self.stmt_defs: Dict[int, Set[str]] = {}     # stmt_id -> variables defined
        self.stmt_uses: Dict[int, Set[str]] = {}     # stmt_id -> variables used
    
    def add_statement(self, stmt_id: int, defines: Set[str], uses: Set[str]):
        """Register a statement with its definitions and uses."""
        self.stmt_defs[stmt_id] = defines
        self.stmt_uses[stmt_id] = uses
        self.dependencies[stmt_id] = set()
        
        # Build dependency edges
        for other_id in self.stmt_defs:
            if other_id == stmt_id:
                continue
            # If other defines something we use, we depend on it
            if self.stmt_defs[other_id] & uses:
                self.dependencies[stmt_id].add(other_id)
    
    def can_swap(self, stmt1_id: int, stmt2_id: int) -> bool:
        """Check if two statements can be safely swapped."""
        # Cannot swap if they have a dependency relationship
        if stmt2_id in self.dependencies.get(stmt1_id, set()):
            return False
        if stmt1_id in self.dependencies.get(stmt2_id, set()):
            return False
        
        # Check for write-after-read, read-after-write, write-after-write conflicts
        defs1 = self.stmt_defs.get(stmt1_id, set())
        uses1 = self.stmt_uses.get(stmt1_id, set())
        defs2 = self.stmt_defs.get(stmt2_id, set())
        uses2 = self.stmt_uses.get(stmt2_id, set())
        
        # Write-after-read: stmt1 uses X, stmt2 defines X
        if uses1 & defs2:
            return False
        # Read-after-write: stmt1 defines X, stmt2 uses X
        if defs1 & uses2:
            return False
        # Write-after-write: both define same variable
        if defs1 & defs2:
            return False
        
        return True

class MutationContext:
    """
    Provides contextual information to mutators.
    This is the "smart" layer that enables safe, semantics-preserving mutations.
    """
    
    def __init__(self, ir: Module):
        self.ir = ir
        self.symbol_table: Dict[str, SymbolInfo] = {}
        self.scopes: List[ScopeInfo] = []
        self.dependency_graph = DependencyGraph()
        
        # Build the context
        self._build_symbol_table()
        self._build_dependency_graph()
    
    def _build_symbol_table(self):
        """Extract all symbols from the IR."""
        # Simple implementation - traverse IR and collect Names
        self._traverse_for_symbols(self.ir)
    
    def _traverse_for_symbols(self, node):
        """Recursively traverse IR to find symbol definitions and uses."""
        if isinstance(node, Name):
            if node.id not in self.symbol_table:
                self.symbol_table[node.id] = SymbolInfo(name=node.id)
            
            # Track usage
            if node.ctx == "Load":
                self.symbol_table[node.id].used_at.append(0)  # Simplified
        
        # Recurse through the IR tree
        if hasattr(node, '__dict__'):
            for value in node.__dict__.values():
                if isinstance(value, list):
                    for item in value:
                        self._traverse_for_symbols(item)
                elif hasattr(value, '__dict__'):
                    self._traverse_for_symbols(value)
    
    def _build_dependency_graph(self):
        """Analyze data flow to build dependency graph."""
        # This is a simplified version - a full implementation would do
        # more sophisticated data flow analysis
        pass
    
    def get_defined_vars(self, node) -> Set[str]:
        """Get all variables defined by this node."""
        defined = set()
        if hasattr(node, 'targets'):  # Assign
            for target in node.targets:
                if isinstance(target, Name):
                    defined.add(target.id)
        elif hasattr(node, 'target'):  # AugAssign, For
            if isinstance(node.target, Name):
                defined.add(node.target.id)
        return defined
    
    def get_used_vars(self, node) -> Set[str]:
        """Get all variables used by this node."""
        used = set()
        self._collect_names(node, used, ctx_filter="Load")
        return used
    
    def _collect_names(self, node, result: Set[str], ctx_filter: str = None):
        """Recursively collect all Name nodes."""
        if isinstance(node, Name):
            if ctx_filter is None or node.ctx == ctx_filter:
                result.add(node.id)
        
        if hasattr(node, '__dict__'):
            for value in node.__dict__.values():
                if isinstance(value, list):
                    for item in value:
                        self._collect_names(item, result, ctx_filter)
                elif hasattr(value, '__dict__'):
                    self._collect_names(value, result, ctx_filter)
