# Transformations

from abc import ABC, abstractmethod

import ast

from ast import AST, NodeVisitor, NodeTransformer


class NodeTransformation(ABC):
    
    def __init__(self, ast: AST) -> None:
        self.ast = ast

    def transform_nodes(self, visitor: NodeVisitor | NodeTransformer) -> None:
        visitor.transform_ast(self.ast)
    
    def get_source(self) -> str:
        ast.fix_missing_locations(self.ast)
        return ast.unparse(self.ast)
