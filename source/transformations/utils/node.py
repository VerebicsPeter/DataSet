# Utility functions for redbaron

# TODO: typing
# TODO: write test cases for utility functions


import redbaron as rb


def __non_formatting_node(node) -> bool:
    return not isinstance(node, (rb.EndlNode, rb.SpaceNode, rb.CommentNode))


def __child_count(node) -> int:
    # return 0 on leaf
    if isinstance(node.value, str): return 0
    # return 1 on single child
    if not isinstance(node.value, (rb.NodeList, rb.ProxyList)): return 1
    # return the length of the filtered proxy list
    return len([x for x in node.value if __non_formatting_node(x)])


def __child_count_recursive(node, type: str) -> int:
    if isinstance(node.value, str): return 0  # return 0 on leaf
    return len(node.value.find_all(type))


def node_assigns(node, name: str) -> bool:
    if isinstance(node, rb.AssignmentNode):
        return node.target.name.value == name
    return False


def node_mentions(node, name: str) -> bool:
    return len(node.find_all('name', value=name)) > 0


def node_is_empty_collection(node) -> bool:
    return isinstance(node, (rb.ListNode, rb.SetNode, rb.DictNode)) and len(node.value) == 0


def node_is_zero_numeric(node) -> bool:
    return isinstance(node, (rb.IntNode, rb.FloatNode)) and node.value in {'0','0.0'}


def match_node(p_node: rb.Node, p_pattern: dict) -> bool:
    """Recursive function to check if a node matches a pattern described in a recursive dictionary.
    
    Args:
        p_node (rb.Node): The node to chek
        p_pattern (dict): The pattern to match

    Returns:
        bool: Returns `True` if the node matched, `False` otherwise
    """
    
    # return false if the typecheck fails
    if not isinstance(p_node, p_pattern['type']):
        return False

    # check attributes if provided
    if p_pattern.get('attr') != None:
        for key in p_pattern['attr']:
            value= p_pattern['attr'][key]
            if (not hasattr(p_node, key) or
                not(getattr(p_node, key) == value)):
                return False
            
    # check target if provided
    if p_pattern.get('target') != None:
        if not hasattr(p_node, 'target'):
            return False
        if not match_node(p_node.target, p_pattern['target']):
            return False

    # * signals that we don't care about the subnodes of a given node
    if p_pattern['nodes'] == '*':
        return True

    # return false if the number of (non formatting) nodes does not match
    if __child_count(p_node) != len(p_pattern['nodes']):
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


def get_last_node_before(node, name: str | None = None, predicate = lambda _node, _name: True) -> (rb.Node | None):
    """Gets the last node before the parameter `node` in the same scope and returns it. Returns `None` if no nodes are before.
    """
    index = node.index_on_parent
    if index is None: return None
    last = None
    for x in node.parent[0 : index]:
        if predicate(x, name): last = x
    return last


def get_last_node_between(node_a, node_b, name: str, predicate = lambda a, b, _name: True) -> rb.Node | None:
    """Gets the last node between the parameters `node_a` and `node_b` in the same scope and returns it. Returns `None` if no such nodes were found.
    """
    if node_a.parent is not node_b.parent: return None
    
    indexes = [node_a.index_on_parent, node_b.index_on_parent]
    s_index = min(indexes)
    e_index = max(indexes)
    parent = node_a.parent
    
    if s_index is None or e_index is None: return None
    
    last = None
    for x in parent[s_index : e_index]:
        if predicate(x, name): last = x
    return last

def get_module_name(ast, module_name: str) -> str | None:
    import_node = ast.find_all('import').find('name', value=module_name)
    
    match import_node:
        case None:
            return None
    match import_node.parent:
        case rb.DottedAsNameNode():
            return import_node.parent.target
        case _:
            return module_name
