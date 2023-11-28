import ast

from ast import AST, NodeVisitor, NodeTransformer

from functools import wraps

from .rules import (
    ForToListComprehension,
    ForToDictComprehension,
    ForToNumpySum,
    InvertIfOrElse,
    RemoveDoubleNegation,
    #DeMorgansLaw # TODO
)


# NOTE: 
# if all transformers are to be refactored into `get_change` - `apply_change` pattern
# a separate `NodeVisitor` can be created to gather the nodes matched,
# this changes the time complexity from n to 2*n


# wrapper function that adds parent attributes
def context_parent(method):
    @wraps(method)
    def wrapper(self, root: AST):
        for node in ast.walk(root):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        method(self, root)
    return wrapper


class ForTransformer(NodeTransformer):
    
    def __init__(
        self,
        rule:
            ForToListComprehension
        |   ForToDictComprehension
        |   ForToNumpySum
        ):
        self.rule = rule
        self.results = []
    
    # Transform the AST in one call
    @context_parent
    def transform_ast(self, node: AST):
        self.__get_results(node)
        self.__set_results()
    
    # Get the results by calling visitor
    def __get_results(self, node: AST) -> None:
        self.results = []
        self.visit(node)
    
    # Apply the results after visiting
    def __set_results(self) -> None:
        if self.results:
            for result in self.results:
                print("Applying:",result)
                result[0].value = result[1]
            # remove the applied results
            self.results = [result for result in self.results if result[0].value != result[1]]
    
    # Visitor for for nodes
    def visit_For(self, node: AST):
        print('-'*150)
        print(ast.dump(node, indent=2))
        
        if not hasattr(node,"parent") or not hasattr(node.parent,"body"):
            return node
        
        parent = node.parent.body
        
        result = self.rule.change(node)
        # if the result matches, do semantic checks and store if possible
        if parent and result:
            i = parent.index(node)
            # leave if the node is the first in a block
            if i < 1:
                return node
            
            id,check = result['id'],result['check']
            if check(parent[i-1], id):
                self.results.append([parent[i-1], result['result']])
                # remove the node from the tree
                return None
        # leave if not matched or no parent set
        return node


class IfTransformer(NodeTransformer):
    
    def __init__(
        self,
        rule:
            InvertIfOrElse
        ):
        self.rule = rule
    
    # Transform the AST
    def transform_ast(self, node: AST):
        self.visit(node)
    
    # Visitor for if nodes
    def visit_If(self, node: AST):
        print('-'*150)
        print(ast.dump(node, indent=2))
        
        result = self.rule.change(node)
        
        if result: return result["result"]
        # leave unchanged        
        return node


class LogicTransformer(NodeTransformer):
    
    def __init__(
        self,
        rule:
            RemoveDoubleNegation
        ):
        self.rule = rule
    
    # Transform the AST
    def transform_ast(self, node: AST):
        self.visit(node)
    
    # Visitor for unary operators
    def visit_UnaryOp(self, node: AST):
        print('-'*150)
        print(ast.dump(node, indent=2))
        
        result = self.rule.change(node)
        
        if result: return result["result"]
        return node
