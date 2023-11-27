import ast

from ast import AST, NodeVisitor, NodeTransformer

from .rules import (
    ForToListComprehension,
    ForToDictComprehension,
    ForToNumpySum,
    InvertIfOrElse,
)

# NOTE: 
# if all transformers are to be refactored into `get_change` - `apply_change` pattern
# a separate `NodeVisitor` can be created to gather the nodes matched,
# this changes the time complexity from n to 2*n


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
    
    
    def transform_ast(self, node: AST):
        self.get_results(node); self.apply_results()
    
    
    def get_results(self, node: AST) -> None:
        if self.has_unapplied(): self.results = []
        self.visit(node)
    
    
    def apply_results(self) -> None:
        if self.has_unapplied():
            for result in self.results:
                print("Applying:",result)
                result[0].value = result[1]
            # remove the applied results
            self.results = [result for result in self.results if result[0].value != result[1]]
    
    
    def has_unapplied(self) -> bool:
        return self.results != []
    
    
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
                # remove the node from the graph
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
    
    
    def transform_ast(self, node: AST):
        self.visit(node)
    
    
    def visit_If(self, node: AST):
        print('-'*150)
        print(ast.dump(node, indent=2))
        
        result = self.rule.change(node)
        
        if result:
            # change the node
            return result["result"]
        # leave unchanged        
        return node
