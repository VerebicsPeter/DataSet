# Transformations

from abc import ABC, abstractmethod

import ast

from ast import AST, NodeVisitor, NodeTransformer

from .visitors import ForTransformer


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

    # TODO
    def get_source_dump(self) -> str:
        return ast.unparse(self.ast)


class ForNodeTransformation(NodeTransformation):

    def __init__(self, ast: AST) -> None:
        super().__init__(ast)
        self.add_parent_attribute()


    def transform_nodes(self, visitor: ForTransformer) -> None:
        visitor.visit(self.ast)
        print('-'*150)
        print("!got results!")
        for result in visitor.results:
            print(result)
            result[0].value = result[1]
        print('-'*150)
