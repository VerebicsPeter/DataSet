# Implementations of for node transformations

# TODO: typing and callable
# TODO: maybe define two methods (get_changes, apply_changes) in transformation classes
# TODO: Tamásnak írni a csoportban a githubos cuccal kapcsolatban


from redbaron import RedBaron, ForNode

from .rules import Rule


class ForNodeTransformation():
    
    def __init__(self, ast: RedBaron, rule: Rule) -> None:
        self.ast  = ast
        self.rule = rule
    
    
    def transform_nodes(self) -> None:
        # print source lines before
        print(self.ast)
        print('-'*150)
        
        for_nodes = self.ast.find_all('for')
        
        for for_node in for_nodes:
            self.transform_node(for_node)
        
        # print source lines after
        print(self.ast)
        changed = self.ast.dumps()  # this is the dump of the changed source code
        print('-'*150)
        print(changed)
        
    
    def transform_node(self, node: ForNode) -> None:
        if not self.rule.match(node): return None    
        # get change
        result = self.rule.change(node)
        # return if there is no change to be applied
        if result is None: return None
        # apply change
        result[0].value = result[1]
        # unlink the for node from ast
        parent = node.parent
        parent.remove(node)
