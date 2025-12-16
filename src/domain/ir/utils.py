"""
IR Traversal and Transformation Utilities.

This module provides the NodeVisitor and NodeTransformer base classes,
patterned after Python's ast module, to facilitate safe and easy
manipulation of the HEDGE IR.
"""
from typing import Any, Optional
from src.domain.ir import schema

class NodeVisitor:
    """
    A node visitor base class that walks the IR tree and calls a
    visitor function for every node found.

    This function may return a value which is forwarded by the `visit` method.

    Methods:
        visit(node): Visit a node.
        generic_visit(node): Called if no explicit visitor function exists for a node.
    """

    def visit(self, node: schema.IRNode) -> Any:
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: schema.IRNode) -> Any:
        """Called if no explicit visitor function exists for a node."""
        if hasattr(node, '__dict__'):
            for field, value in node.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, schema.IRNode):
                            self.visit(item)
                elif isinstance(value, schema.IRNode):
                    self.visit(value)

class NodeTransformer(NodeVisitor):
    """
    A :class:`NodeVisitor` subclass that walks the IR tree and allows
    modification of nodes.

    The `visit` method returns the modified node (or None if the node should be deleted).
    """

    def generic_visit(self, node: schema.IRNode) -> schema.IRNode:
        if hasattr(node, '__dict__'):
            for field, value in node.__dict__.items():
                if isinstance(value, list):
                    new_values = []
                    for item in value:
                        if isinstance(item, schema.IRNode):
                            new_node = self.visit(item)
                            if new_node is None:
                                continue
                            elif isinstance(new_node, list):
                                new_values.extend(new_node)
                            else:
                                new_values.append(new_node)
                        else:
                            new_values.append(item)
                    setattr(node, field, new_values)
                elif isinstance(value, schema.IRNode):
                    new_node = self.visit(value)
                    if new_node is None:
                        delattr(node, field)
                    else:
                        setattr(node, field, new_node)
        return node
