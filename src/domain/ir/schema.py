"""
Strict Intermediate Representation (IR) Schema.

This module defines a fully-typed, structural IR for Python code.
Unlike traditional "stringly-typed" representations, every expression
and statement is represented as a strongly-typed Pydantic model.

This enables:
- Type-safe mutations
- Structural validation
- Deterministic code generation
- Safe program transformations
"""
from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict

# --- Base Nodes ---

class IRNode(BaseModel):
    """
    Base class for all IR nodes.
    
    All IR nodes are immutable Pydantic models that can be:
    - Serialized to JSON
    - Validated at runtime
    - Deep-copied for mutations
    """
    
    model_config = ConfigDict(frozen=False)  # Allow mutations during transformation

class Expression(IRNode):
    """
    Base class for all expressions.
    
    Expressions are nodes that evaluate to a value.
    Examples: BinaryOp, Call, Name, Constant
    """
    pass

class Statement(IRNode):
    """
    Base class for all statements.
    
    Statements are nodes that perform actions but don't return values.
    Examples: Assign, Return, If, While, For
    """
    pass

# --- Expressions ---

class Constant(Expression):
    value: Union[int, float, str, bool, None]
    kind: Literal["int", "float", "str", "bool", "None"]

class Name(Expression):
    id: str
    ctx: Literal["Load", "Store", "Del"] = "Load"

class BinaryOp(Expression):
    left: Expression
    op: str  # +, -, *, /, etc.
    right: Expression

class UnaryOp(Expression):
    op: str  # not, -, +, ~
    operand: Expression

class BoolOp(Expression):
    op: str  # and, or
    values: List[Expression]

class Compare(Expression):
    left: Expression
    ops: List[str]
    comparators: List[Expression]

class Call(Expression):
    func: Expression
    args: List[Expression]
    keywords: List[tuple[str, Expression]] = Field(default_factory=list)

class Attribute(Expression):
    value: Expression
    attr: str
    ctx: Literal["Load", "Store", "Del"] = "Load"

class Subscript(Expression):
    value: Expression
    slice: Expression
    ctx: Literal["Load", "Store", "Del"] = "Load"

class ListExpr(Expression):
    elts: List[Expression]
    ctx: Literal["Load", "Store", "Del"] = "Load"

class TupleExpr(Expression):
    elts: List[Expression]
    ctx: Literal["Load", "Store", "Del"] = "Load"

class DictExpr(Expression):
    keys: List[Optional[Expression]]
    values: List[Expression]

class SetExpr(Expression):
    elts: List[Expression]
    ctx: Literal["Load", "Store", "Del"] = "Load"

class Lambda(Expression):
    args: List[str]
    body: Expression

class Yield(Expression):
    value: Optional[Expression] = None

class YieldFrom(Expression):
    value: Expression

# --- Statements ---

class Assign(Statement):
    targets: List[Expression]
    value: Expression

class AugAssign(Statement):
    target: Expression
    op: str
    value: Expression

class AnnAssign(Statement):
    target: Expression
    annotation: Expression
    value: Optional[Expression] = None
    simple: int = 1

class Return(Statement):
    value: Optional[Expression] = None

class Pass(Statement):
    pass

class Break(Statement):
    pass

class Continue(Statement):
    pass

class ExprStmt(Statement):
    value: Expression

class Block(IRNode):
    statements: List[Statement]

class If(Statement):
    test: Expression
    body: Block
    orelse: Optional[Block] = None

class While(Statement):
    test: Expression
    body: Block
    orelse: Optional[Block] = None

class For(Statement):
    target: Expression
    iter: Expression
    body: Block
    orelse: Optional[Block] = None

class FunctionDef(Statement):
    name: str
    args: List[str]  # Simplified for now, can be expanded to full arguments object
    body: Block
    decorator_list: List[Expression] = Field(default_factory=list)
    returns: Optional[Expression] = None

class ClassDef(Statement):
    name: str
    bases: List[Expression]
    keywords: List[tuple[str, Expression]] = Field(default_factory=list)
    body: Block
    decorator_list: List[Expression] = Field(default_factory=list)

class Import(Statement):
    names: List[tuple[str, Optional[str]]]  # (name, asname)

class ImportFrom(Statement):
    module: Optional[str]
    names: List[tuple[str, Optional[str]]]  # (name, asname)
    level: int = 0

class ExceptHandler(IRNode):
    type: Optional[Expression] = None
    name: Optional[str] = None
    body: Block

class Try(Statement):
    body: Block
    handlers: List[ExceptHandler]
    orelse: Optional[Block] = None
    finalbody: Optional[Block] = None

class WithItem(IRNode):
    context_expr: Expression
    optional_vars: Optional[Expression] = None

class With(Statement):
    items: List[WithItem]
    body: Block

# --- Top Level ---

class Module(IRNode):
    body: Block

# --- Rebuild Models for Forward Refs ---
Block.model_rebuild()
If.model_rebuild()
While.model_rebuild()
For.model_rebuild()
Try.model_rebuild()
With.model_rebuild()
ExceptHandler.model_rebuild()
FunctionDef.model_rebuild()
ClassDef.model_rebuild()
