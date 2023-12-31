# Helper functions for transformations

from ast import AST, NodeVisitor

import ast


class NameVisitor(NodeVisitor):
    
    def get_names(self, node: AST, id: str = None) -> list:
        self._id    = id
        self._names = []
        self.visit(node)
        return self._names

    def visit_Name(self, node: ast.Name):
        match self._id:
            case None:
                self._names.append(node)
            case id:
                if id != node.id: return
                self._names.append(node)


class Node:
    
    @staticmethod
    def all_names(node: AST, id: str = None):
        """Returns a list the list of all `ast.Name` nodes inside `node`.
        """
        visitor = NameVisitor()
        mentions = visitor.get_names(node, id)
        return mentions
    
    @staticmethod
    def has_names(node: AST, id: str = None) -> bool:
        visitor = NameVisitor()
        mentions = visitor.get_names(node, id)
        return bool(len(mentions))
