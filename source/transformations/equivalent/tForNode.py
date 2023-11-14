# Implementations of for node transformations transformations

# TODO: typing and callable
# TODO: maybe define two methods (get_changes, apply_changes) in transformation classes
# TODO: Tamásnak írni a csoportban a githubos cuccal kapcsolatban


from redbaron import RedBaron, ForNode

from .rules import Rule


class ForNodeTransformation():

    def __init__(self, node: ForNode, rule: Rule) -> None:
        self.node = node
        self.rule = rule
    
    def transform_node(self) -> None:
        # print source lines before
        print(self.node)
        print('-'*150)
        
        if self.rule.match(self.node):
            result = self.rule.change(self.node)
            
            if result is None:
                return
            else:
                # apply the change
                result[0].value = result[1]
                # unlink the for node
                parent = self.node.parent
                parent.remove(self.node)
            
        # print source lines after
        print(self.node)
        changed = self.node.dumps()  # this is the dump of the changed source code
        print('-'*150)
        print(changed)


class ForNodesTransformation():
    
    def __init__(self, ast: RedBaron, rule: Rule) -> None:
        self.ast  = ast
        self.rule = rule
    
    def transform_nodes(self) -> None:
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
