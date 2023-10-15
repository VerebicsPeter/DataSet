# Utility functions for redbaron


import redbaron as rb


def not_formatting_node(node) -> bool:
    return not isinstance(node, (rb.EndlNode, rb.SpaceNode, rb.CommentNode))


def child_count(node) -> int:
    if isinstance(node.value, str): return 0  # return 0 on leaf
    return len([x for x in node.value if not_formatting_node(x)])


def child_count_rec(node, child_type: str | None = None) -> int:
    if isinstance(node.value, str): return 0  # return 0 on leaf
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


# IDEA:
# instead of writing different functions for checking each pattern
# write a recursive function that checks a recursive dict representing a pattern
def match_node(p_node: rb.Node, p_pattern: dict) -> bool:
    if not isinstance(p_node, p_pattern['type']):
        return False
    
    # * signals that we don't care about the subnodes of a given node
    if p_pattern['nodes'] == '*':
        return True

    if child_count(p_node) != len(p_pattern['nodes']):
        return False

    if isinstance(p_node.value, str):
        return True

    for node, pattern in zip(p_node.value, p_pattern['nodes']):
        if not match_node(node, pattern): return False

    return True
