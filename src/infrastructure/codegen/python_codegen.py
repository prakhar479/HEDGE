from typing import List
from src.domain.ir import schema

class PythonCodeGenerator:
    """
    Converts Strict IR back into executable Python code.
    """
    
    def generate(self, module: schema.Module) -> str:
        return self._generate_block(module.body, indent=0)
    
    def _generate_block(self, block: schema.Block, indent: int) -> str:
        lines = []
        for stmt in block.statements:
            lines.append(self._generate_stmt(stmt, indent))
        return "\n".join(lines)
    
    def _indent(self, indent: int) -> str:
        return "    " * indent
    
    def _generate_stmt(self, stmt: schema.Statement, indent: int) -> str:
        prefix = self._indent(indent)
        
        if isinstance(stmt, schema.Assign):
            targets = [self._generate_expr(t) for t in stmt.targets]
            value = self._generate_expr(stmt.value)
            return f"{prefix}{' = '.join(targets)} = {value}"
        
        elif isinstance(stmt, schema.AnnAssign):
            target = self._generate_expr(stmt.target)
            annotation = self._generate_expr(stmt.annotation)
            if stmt.value:
                value = self._generate_expr(stmt.value)
                return f"{prefix}{target}: {annotation} = {value}"
            return f"{prefix}{target}: {annotation}"
            
        elif isinstance(stmt, schema.AugAssign):
            target = self._generate_expr(stmt.target)
            value = self._generate_expr(stmt.value)
            return f"{prefix}{target} {stmt.op}= {value}"
            
        elif isinstance(stmt, schema.Return):
            if stmt.value:
                return f"{prefix}return {self._generate_expr(stmt.value)}"
            return f"{prefix}return"
            
        elif isinstance(stmt, schema.Pass):
            return f"{prefix}pass"
        elif isinstance(stmt, schema.Break):
            return f"{prefix}break"
        elif isinstance(stmt, schema.Continue):
            return f"{prefix}continue"
            
        elif isinstance(stmt, schema.ExprStmt):
            return f"{prefix}{self._generate_expr(stmt.value)}"
            
        elif isinstance(stmt, schema.If):
            test = self._generate_expr(stmt.test)
            lines = [f"{prefix}if {test}:"]
            lines.append(self._generate_block(stmt.body, indent + 1))
            if stmt.orelse:
                lines.append(f"{prefix}else:")
                lines.append(self._generate_block(stmt.orelse, indent + 1))
            return "\n".join(lines)
            
        elif isinstance(stmt, schema.While):
            test = self._generate_expr(stmt.test)
            lines = [f"{prefix}while {test}:"]
            lines.append(self._generate_block(stmt.body, indent + 1))
            if stmt.orelse:
                lines.append(f"{prefix}else:")
                lines.append(self._generate_block(stmt.orelse, indent + 1))
            return "\n".join(lines)
            
        elif isinstance(stmt, schema.For):
            target = self._generate_expr(stmt.target)
            iter_ = self._generate_expr(stmt.iter)
            lines = [f"{prefix}for {target} in {iter_}:"]
            lines.append(self._generate_block(stmt.body, indent + 1))
            if stmt.orelse:
                lines.append(f"{prefix}else:")
                lines.append(self._generate_block(stmt.orelse, indent + 1))
            return "\n".join(lines)
            
        elif isinstance(stmt, schema.FunctionDef):
            args = ", ".join(stmt.args)
            lines = []
            for dec in stmt.decorator_list:
                lines.append(f"{prefix}@{self._generate_expr(dec)}")
            
            ret = f" -> {self._generate_expr(stmt.returns)}" if stmt.returns else ""
            lines.append(f"{prefix}def {stmt.name}({args}){ret}:")
            lines.append(self._generate_block(stmt.body, indent + 1))
            return "\n".join(lines)
            
        elif isinstance(stmt, schema.ClassDef):
            bases = ", ".join([self._generate_expr(b) for b in stmt.bases])
            bases_str = f"({bases})" if bases else ""
            lines = []
            for dec in stmt.decorator_list:
                lines.append(f"{prefix}@{self._generate_expr(dec)}")
            
            lines.append(f"{prefix}class {stmt.name}{bases_str}:")
            lines.append(self._generate_block(stmt.body, indent + 1))
            return "\n".join(lines)
            
        elif isinstance(stmt, schema.Import):
            names = [f"{n} as {a}" if a else n for n, a in stmt.names]
            return f"{prefix}import {', '.join(names)}"
            
        elif isinstance(stmt, schema.ImportFrom):
            names = [f"{n} as {a}" if a else n for n, a in stmt.names]
            module = stmt.module or ""
            dots = "." * stmt.level
            return f"{prefix}from {dots}{module} import {', '.join(names)}"
            
        return f"{prefix}# Unsupported statement: {type(stmt).__name__}"

    def _generate_expr(self, expr: schema.Expression) -> str:
        if isinstance(expr, schema.Constant):
            if expr.kind == "str":
                return repr(expr.value)
            return str(expr.value)
            
        elif isinstance(expr, schema.Name):
            return expr.id
            
        elif isinstance(expr, schema.BinaryOp):
            left = self._generate_expr(expr.left)
            right = self._generate_expr(expr.right)
            return f"({left} {expr.op} {right})"
            
        elif isinstance(expr, schema.UnaryOp):
            operand = self._generate_expr(expr.operand)
            if expr.op in ["not"]:
                return f"({expr.op} {operand})"
            return f"{expr.op}{operand}"
            
        elif isinstance(expr, schema.BoolOp):
            values = [self._generate_expr(v) for v in expr.values]
            return f"({f' {expr.op} '.join(values)})"
            
        elif isinstance(expr, schema.Compare):
            left = self._generate_expr(expr.left)
            comparisons = []
            for op, comp in zip(expr.ops, expr.comparators):
                comparisons.append(f"{op} {self._generate_expr(comp)}")
            return f"({left} {' '.join(comparisons)})"
            
        elif isinstance(expr, schema.Call):
            func = self._generate_expr(expr.func)
            args = [self._generate_expr(a) for a in expr.args]
            keywords = [f"{k}={self._generate_expr(v)}" for k, v in expr.keywords]
            all_args = ", ".join(args + keywords)
            return f"{func}({all_args})"
            
        elif isinstance(expr, schema.Attribute):
            value = self._generate_expr(expr.value)
            return f"{value}.{expr.attr}"
            
        elif isinstance(expr, schema.Subscript):
            value = self._generate_expr(expr.value)
            slice_ = self._generate_expr(expr.slice)
            return f"{value}[{slice_}]"
            
        elif isinstance(expr, schema.ListExpr):
            elts = [self._generate_expr(e) for e in expr.elts]
            return f"[{', '.join(elts)}]"
            
        elif isinstance(expr, schema.TupleExpr):
            elts = [self._generate_expr(e) for e in expr.elts]
            if len(elts) == 1:
                return f"({elts[0]},)"
            return f"({', '.join(elts)})"
            
        elif isinstance(expr, schema.DictExpr):
            items = []
            for k, v in zip(expr.keys, expr.values):
                key = self._generate_expr(k) if k else "None"
                val = self._generate_expr(v)
                items.append(f"{key}: {val}")
            return f"{{{', '.join(items)}}}"
            
        return f"<Unsupported Expr: {type(expr).__name__}>"
