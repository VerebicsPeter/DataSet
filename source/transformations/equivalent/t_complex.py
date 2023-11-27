# Transformations

# TODO: factories for `NodeTransformation` derived classes


from abc import ABC, abstractmethod

import ast

from ast import AST, NodeVisitor, NodeTransformer

from .visitors import ForTransformer, IfTransformer


class NodeTransformation(ABC):

    def __init__(self, ast: AST):
        self.ast = ast

    def add_parent_attribute(self) -> None:
        for node in ast.walk(self.ast):
            for child in ast.iter_child_nodes(node):
                child.parent = node

    @abstractmethod
    def transform_nodes(self, visitor: NodeVisitor | NodeTransformer) -> None:
        pass

    def get_source(self) -> str:
        return ast.unparse(self.ast)


class ForTransformation(NodeTransformation):

    def __init__(self, ast: AST) -> None:
        super().__init__(ast)
        self.add_parent_attribute()

    def transform_nodes(self, visitor: ForTransformer) -> None:
        print('-'*150)
        visitor.transform_ast(self.ast)
        print('-'*150)


class IfTransformation(NodeTransformation):

    def __init__(self, ast: AST):
        super().__init__(ast)

    def transform_nodes(self, visitor: IfTransformer):
        print('-'*150)
        visitor.transform_ast(self.ast)
        print('-'*150)

