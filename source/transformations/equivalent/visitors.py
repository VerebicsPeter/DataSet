import ast

from ast import AST, Assign, NodeVisitor, NodeTransformer

from .rules import Rule


class ForTransformer(NodeTransformer):
    
    def __init__(self, rule: Rule):
        self.rule = rule
        self.results = []
    
    def visi_Assign(self, node: AST):    
        return node
    
    # Visit for nodes
    def visit_For(self, node: AST):
        print('-'*150)
        print(ast.dump(node, indent=2))
        
        parent = node.parent.body
        
        if not parent: return node
        
        result = self.rule.change(node)
        # if the result matches, do semantic checks and apply it if possible
        if result and parent:
            i = parent.index(node)
            if i < 1: return node
            
            id,check = result['id'], result['check']
            if check(parent[i-1], id):
                self.results.append([parent[i-1], result['result']])
                return None
            
        return node
    
    def __assigns_empty_dict(self, node: AST, _id: str) -> bool:
        pass
    
    def __assigns_empty_set(self, node: AST, _id: str) -> bool:
        pass
