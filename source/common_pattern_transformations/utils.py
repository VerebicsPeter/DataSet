# Utility functions for redbaron

import redbaron as rb

def node_count(node, child_type: str) -> int:
    # return 0 on leaf
    if isinstance(node.value, str): return 0
    return len(node.value.find_all(child_type))

def node_mentions(node, name: str) -> bool:
    return len(node.find_all('name', value=name)) > 0

def node_is_assignment_to(node, name: str) -> bool:
    if isinstance(node, rb.AssignmentNode):
        return node.target.name.value == name
    return False

def get_last_node_before(node, name = None, predicate = lambda _node, _name: True) -> (rb.Node | None):
    index = node.index_on_parent
    if index is None: return None
    last = None
    for x in node.parent[0:index]:
        if predicate(x, name): last = x
    return last
