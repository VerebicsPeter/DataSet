import ast

from ast import AST, NodeVisitor, NodeTransformer

from .rules import Rule


class ForTransformer(NodeTransformer):
    
    def __init__(self, rule: Rule):
        self.rule = rule
        self.results = []
    
    
    def has_unapplied(self) -> bool:
        return self.results != []
    
    
    def get_results(self, node: AST) -> None:
        if self.has_unapplied(): self.results = []
        self.visit(node)
    
    
    def apply_results(self) -> None:
        if self.has_unapplied():
            for result in self.results:
                print("Applying:",result)
                result[0].value = result[1]
            self.results = [result for result in self.results if result[0].value != result[1]]
    
    # Visitor for assignment nodes
    def visit_Assign(self, node: AST):    
        return node
    
    # Visitor for for nodes
    def visit_For(self, node: AST):
        print('-'*150)
        print(ast.dump(node, indent=2))
        
        if not hasattr(node,"parent") or not hasattr(node.parent,"body"):
            return node
                
        parent = node.parent.body
        
        result = self.rule.change(node)
        # if the result matches, do semantic checks and apply it if possible
        if parent and result:
            i = parent.index(node)
            if i < 1: return node
            
            id,check = result['id'],result['check']
            if check(parent[i-1], id):
                self.results.append([parent[i-1], result['result']])
                return None
        return node
