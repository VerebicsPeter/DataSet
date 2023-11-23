# Script to muck about with ast and redbaron

from redbaron import RedBaron, EndlNode, NodeList

source = """

class ForToListComprehension(Rule):
    
    # comment, comment, comment
    
    def match(self, node: ForNode) -> bool:
    
    
        return (
            
            match_node(node, for_to_list_comprehension)
            
            or
            
            match_node(node, for_to_list_comprehension_if)
            
            or
            
            match_node(node, mypattern)
            
        )
    
    def change(self, node: ForNode) -> tuple | None:
        change = ForToListComprehensionChange(node)
        return change.get_change()
        # hello world

"""

red = RedBaron(source)

print(red.node_list)
print('-'*150)

endlines = red.find_all('endl')

for endline in endlines:
    if not isinstance(endline.previous, EndlNode): continue
    p      = endline.parent
    parent = p.node_list if isinstance(p, RedBaron) else p
    if len(parent) > 1 and endline in parent:
        parent.remove(endline)

print(red.node_list)
print('-'*150)

print(red.dumps())
print('-'*150)
