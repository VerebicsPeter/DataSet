# Transformations

# TODO: abstract factory for `NodeTransformation` derived classes


from abc import ABC, abstractmethod

import ast

from ast import AST, NodeVisitor, NodeTransformer


class NodeTransformation(ABC):

    def __init__(self, ast: AST) -> None:
        self.ast = ast

    def transform_nodes(self, visitor: NodeVisitor | NodeTransformer) -> None:
        print('-'*150)
        visitor.transform_ast(self.ast)
        print('-'*150)

    def get_source(self) -> str:
        return ast.unparse(self.ast)
