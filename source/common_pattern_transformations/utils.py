# TODO: write test cases for utility functions

# Utility functions for redbaron

import redbaron as rb


def _not_formatting_node(node) -> bool:
    return not isinstance(node, (rb.EndlNode, rb.SpaceNode, rb.CommentNode))


def _child_count(node) -> int:
    # return 0 on leaf
    if isinstance(node.value, str): return 0
    # return 1 on single child
    if not isinstance(node.value, (rb.NodeList, rb.ProxyList)): return 1
    # return the length of the filtered proxy list
    return len([x for x in node.value if _not_formatting_node(x)])


def _child_count_rec(node, child_type: str | None = None) -> int:
    if isinstance(node.value, str): return 0  # return 0 on leaf
    return len(node.value.find_all(child_type))


def node_mentions(node, name: str) -> bool:
    return len(node.find_all('name', value=name)) > 0


def node_is_assignment_to(node, name: str) -> bool:
    if isinstance(node, rb.AssignmentNode):
        return node.target.name.value == name
    return False


def node_is_empty_list(node) -> bool:
    return isinstance(node, rb.ListNode) and len(node.value) == 0


def get_last_node_before(node, name = None, predicate = lambda _node, _name: True) -> (rb.Node | None):
    index = node.index_on_parent
    if index is None: return None
    last = None
    for x in node.parent[0:index]:
        if predicate(x, name): last = x
    return last


# IDEA:
# instead writing different functions for checking each pattern
# write a recursive function that checks a recursive dict representing a pattern
def match_node(p_node: rb.Node, p_pattern: dict) -> bool:
    # return false if the typecheck fails
    if not isinstance(p_node, p_pattern['type']):
        return False
    
    # * signals that we don't care about the subnodes of a given node
    if p_pattern['nodes'] == '*':
        return True

    # return false if the number of (not formatting) nodes doesn not match
    if _child_count(p_node) != len(p_pattern['nodes']):
        return False

    # return true on leaf
    if isinstance(p_node.value, str):
        return True
    
    # return recursive call on single child
    if not isinstance(p_node.value, (rb.NodeList, rb.ProxyList)):
        node, pattern=p_node.value, p_pattern['nodes'][0]
        return match_node(node, pattern)

    # return false if match fails on child
    for node, pattern in zip(p_node.value, p_pattern['nodes']):
        if not match_node(node, pattern): return False

    return True
