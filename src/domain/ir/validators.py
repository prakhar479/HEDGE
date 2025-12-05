from typing import List, Set
from src.domain.ir import schema

class ValidationResult:
    def __init__(self, valid: bool, errors: List[str] = None):
        self.valid = valid
        self.errors = errors or []

class IRValidator:
    """
    Validates the structural and semantic integrity of the IR.
    """
    
    def validate(self, module: schema.Module) -> ValidationResult:
        errors = []
        
        # 1. Symbol Table Check (Basic)
        # Ensure no duplicate function names at top level
        func_names: Set[str] = set()
        for stmt in module.body.statements:
            if isinstance(stmt, schema.FunctionDef):
                if stmt.name in func_names:
                    errors.append(f"Duplicate function name: {stmt.name}")
                func_names.add(stmt.name)
        
        # 2. Scope Check (Basic)
        # Ensure 'return', 'break', 'continue' are inside appropriate blocks
        # This requires a recursive visitor.
        scope_errors = self._check_scopes(module)
        errors.extend(scope_errors)
        
        return ValidationResult(len(errors) == 0, errors)

    def _check_scopes(self, module: schema.Module) -> List[str]:
        errors = []
        
        class ScopeVisitor:
            def __init__(self):
                self.in_loop = 0
                self.in_func = 0
                self.errors = []
            
            def visit_block(self, block: schema.Block):
                for stmt in block.statements:
                    self.visit_stmt(stmt)
            
            def visit_stmt(self, stmt: schema.Statement):
                if isinstance(stmt, schema.Return):
                    if self.in_func == 0:
                        self.errors.append("Return statement outside function")
                elif isinstance(stmt, (schema.Break, schema.Continue)):
                    if self.in_loop == 0:
                        self.errors.append("Break/Continue statement outside loop")
                elif isinstance(stmt, schema.FunctionDef):
                    self.in_func += 1
                    self.visit_block(stmt.body)
                    self.in_func -= 1
                elif isinstance(stmt, (schema.For, schema.While)):
                    self.in_loop += 1
                    self.visit_block(stmt.body)
                    if stmt.orelse:
                        self.visit_block(stmt.orelse)
                    self.in_loop -= 1
                elif isinstance(stmt, schema.If):
                    self.visit_block(stmt.body)
                    if stmt.orelse:
                        self.visit_block(stmt.orelse)
                # Recurse for other container statements if added
        
        visitor = ScopeVisitor()
        visitor.visit_block(module.body)
        return visitor.errors
