# Implementations of assignment node transformations


from redbaron import RedBaron, AssignmentNode

from .rules import Rule


class AssignmentNodeTransformation():
    
    def __init__(self, ast: RedBaron, rule: Rule):
        self.ast  = ast
        self.rule = rule
    
    
    def transform_node(self, node: AssignmentNode) -> None:
        if not self.rule.match(node): return None
        result = self.rule.change(node)
        if result is None: return None
     
        
    def transform_nodes(self) -> None:
        # print source lines before
        print(self.ast)
        print('-'*150)
        
        nodes = self.ast.find_all('assignment')
        
        for node in nodes:
            self.transform_node(node)
        
        # print source lines after
        print(self.ast)
        changed = self.ast.dumps()  # this is the dump of the changed source code
        print('-'*150)
        print(changed)

