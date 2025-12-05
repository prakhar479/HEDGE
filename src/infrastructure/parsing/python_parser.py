import ast
from typing import List, Optional, Any
from src.domain.ir import schema

class PythonParser:
    """
    Converts Python source code (via AST) into Strict IR.
    """
    
    def parse(self, code: str) -> schema.Module:
        tree = ast.parse(code)
        return self._visit_module(tree)
    
    def _visit_module(self, node: ast.Module) -> schema.Module:
        return schema.Module(body=self._visit_block(node.body))
    
    def _visit_block(self, stmts: List[ast.stmt]) -> schema.Block:
        ir_stmts = []
        for stmt in stmts:
            ir_stmt = self._visit_stmt(stmt)
            if ir_stmt:
                ir_stmts.append(ir_stmt)
        return schema.Block(statements=ir_stmts)

    def _visit_stmt(self, node: ast.stmt) -> Optional[schema.Statement]:
        if isinstance(node, ast.Assign):
            return schema.Assign(
                targets=[self._visit_expr(t) for t in node.targets],
                value=self._visit_expr(node.value)
            )
        elif isinstance(node, ast.AnnAssign):
            return schema.AnnAssign(
                target=self._visit_expr(node.target),
                annotation=self._visit_expr(node.annotation),
                value=self._visit_expr(node.value) if node.value else None,
                simple=node.simple
            )
        elif isinstance(node, ast.AugAssign):
            return schema.AugAssign(
                target=self._visit_expr(node.target),
                op=self._get_op_name(node.op),
                value=self._visit_expr(node.value)
            )
        elif isinstance(node, ast.Return):
            return schema.Return(value=self._visit_expr(node.value) if node.value else None)
        elif isinstance(node, ast.Pass):
            return schema.Pass()
        elif isinstance(node, ast.Break):
            return schema.Break()
        elif isinstance(node, ast.Continue):
            return schema.Continue()
        elif isinstance(node, ast.Expr):
            return schema.ExprStmt(value=self._visit_expr(node.value))
        elif isinstance(node, ast.If):
            return schema.If(
                test=self._visit_expr(node.test),
                body=self._visit_block(node.body),
                orelse=self._visit_block(node.orelse) if node.orelse else None
            )
        elif isinstance(node, ast.While):
            return schema.While(
                test=self._visit_expr(node.test),
                body=self._visit_block(node.body),
                orelse=self._visit_block(node.orelse) if node.orelse else None
            )
        elif isinstance(node, ast.For):
            return schema.For(
                target=self._visit_expr(node.target),
                iter=self._visit_expr(node.iter),
                body=self._visit_block(node.body),
                orelse=self._visit_block(node.orelse) if node.orelse else None
            )
        elif isinstance(node, ast.FunctionDef):
            return schema.FunctionDef(
                name=node.name,
                args=[arg.arg for arg in node.args.args], # Simplified
                body=self._visit_block(node.body),
                decorator_list=[self._visit_expr(d) for d in node.decorator_list],
                returns=self._visit_expr(node.returns) if node.returns else None
            )
        elif isinstance(node, ast.ClassDef):
            return schema.ClassDef(
                name=node.name,
                bases=[self._visit_expr(b) for b in node.bases],
                keywords=[(k.arg, self._visit_expr(k.value)) for k in node.keywords],
                body=self._visit_block(node.body),
                decorator_list=[self._visit_expr(d) for d in node.decorator_list]
            )
        elif isinstance(node, ast.Import):
            return schema.Import(names=[(n.name, n.asname) for n in node.names])
        elif isinstance(node, ast.ImportFrom):
            return schema.ImportFrom(
                module=node.module,
                names=[(n.name, n.asname) for n in node.names],
                level=node.level
            )
        return None # Unsupported statement

    def _visit_expr(self, node: ast.expr) -> schema.Expression:
        if isinstance(node, ast.Constant):
            kind = "None"
            if isinstance(node.value, bool): kind = "bool"
            elif isinstance(node.value, int): kind = "int"
            elif isinstance(node.value, float): kind = "float"
            elif isinstance(node.value, str): kind = "str"
            return schema.Constant(value=node.value, kind=kind)
        elif isinstance(node, ast.Name):
            return schema.Name(id=node.id, ctx=type(node.ctx).__name__)
        elif isinstance(node, ast.BinOp):
            return schema.BinaryOp(
                left=self._visit_expr(node.left),
                op=self._get_op_name(node.op),
                right=self._visit_expr(node.right)
            )
        elif isinstance(node, ast.UnaryOp):
            return schema.UnaryOp(
                op=self._get_op_name(node.op),
                operand=self._visit_expr(node.operand)
            )
        elif isinstance(node, ast.BoolOp):
            return schema.BoolOp(
                op=self._get_op_name(node.op),
                values=[self._visit_expr(v) for v in node.values]
            )
        elif isinstance(node, ast.Compare):
            return schema.Compare(
                left=self._visit_expr(node.left),
                ops=[self._get_op_name(op) for op in node.ops],
                comparators=[self._visit_expr(c) for c in node.comparators]
            )
        elif isinstance(node, ast.Call):
            return schema.Call(
                func=self._visit_expr(node.func),
                args=[self._visit_expr(a) for a in node.args],
                keywords=[(k.arg, self._visit_expr(k.value)) for k in node.keywords]
            )
        elif isinstance(node, ast.Attribute):
            return schema.Attribute(
                value=self._visit_expr(node.value),
                attr=node.attr,
                ctx=type(node.ctx).__name__
            )
        elif isinstance(node, ast.Subscript):
            return schema.Subscript(
                value=self._visit_expr(node.value),
                slice=self._visit_expr(node.slice),
                ctx=type(node.ctx).__name__
            )
        elif isinstance(node, ast.List):
            return schema.ListExpr(
                elts=[self._visit_expr(e) for e in node.elts],
                ctx=type(node.ctx).__name__
            )
        elif isinstance(node, ast.Tuple):
            return schema.TupleExpr(
                elts=[self._visit_expr(e) for e in node.elts],
                ctx=type(node.ctx).__name__
            )
        elif isinstance(node, ast.Dict):
            return schema.DictExpr(
                keys=[self._visit_expr(k) if k else None for k in node.keys],
                values=[self._visit_expr(v) for v in node.values]
            )
        
        # Fallback for unsupported expressions
        return schema.Constant(value=f"<Unsupported: {type(node).__name__}>", kind="str")

    def _get_op_name(self, op: Any) -> str:
        op_map = {
            ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/',
            ast.Mod: '%', ast.Pow: '**', ast.FloorDiv: '//',
            ast.Eq: '==', ast.NotEq: '!=', ast.Lt: '<', ast.LtE: '<=',
            ast.Gt: '>', ast.GtE: '>=', ast.Is: 'is', ast.IsNot: 'is not',
            ast.In: 'in', ast.NotIn: 'not in',
            ast.And: 'and', ast.Or: 'or',
            ast.Not: 'not', ast.Invert: '~', ast.UAdd: '+', ast.USub: '-'
        }
        return op_map.get(type(op), '?')
