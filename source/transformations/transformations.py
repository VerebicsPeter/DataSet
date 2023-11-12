# Implementations of code transformations

# NOTE: Use 'match ... case' for readability
# TODO: typing and callable
# TODO: maybe define two methods (get_changes, apply_changes) in transformation classes
# Other
# TODO: Tamásnak írni a csoportban a githubos cuccal kapcsolatban

from redbaron import RedBaron

from rules import Rule


class ForNodeTransformation():
    
    def __init__(self, ast: RedBaron, rule: Rule) -> None:
        self.ast    = ast
        self.rule   = rule
    
    def transform_nodes(self):
        # print source lines before
        print(self.ast)
        print('-'*150)
        
        for_nodes = self.ast.find_all('for')
        
        for for_node in for_nodes:
            # skip if node does not match
            if not self.rule.match(for_node): continue
            
            # get change
            result = self.rule.change(for_node)
            # skip if there is no change to be applied
            if result is None: continue
            
            # apply the change
            result[0].value = result[1]
            # unlink the for node
            parent = for_node.parent
            parent.remove(for_node)
        
        # print source lines after
        print(self.ast)
        changed = self.ast.dumps()  # this is the dump of the changed source code
        print('-'*150)
        print(changed)
