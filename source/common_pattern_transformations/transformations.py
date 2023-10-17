# NOTE: Use 'match ... case' for readability

import redbaron as rb

from utils import match_node, node_mentions, node_is_assignment_to, node_is_empty_list, get_last_node_before
from patterns import for_to_listc, for_to_listc_if


# for to list comprehension match
def _t_for_to_listc_match(for_node) -> bool:
    return match_node(for_node, for_to_listc)

# for to list comprehension change
def _t_for_to_listc_change(for_node) -> tuple | None:
    if not _t_for_to_listc_match(for_node):  return None
    
    atomtrailers = for_node.value.find('atomtrailers')
    l_name_nodes = atomtrailers.value.find_all('name')

    if l_name_nodes[1].name.value != 'append': return None
    
    list_name = l_name_nodes[0].name.value

    assignment = get_last_node_before(for_node, list_name, node_is_assignment_to)
    lastmention = get_last_node_before(for_node, list_name, node_mentions)

    if (assignment is None or assignment is not lastmention or not node_is_empty_list(assignment.value)):
        return None
    
    iterator, target = for_node.iterator, for_node.target
    call = atomtrailers.value.find('call')

    if not len(call.value) == 1:
        return None
    if not node_mentions(call, iterator.value):
        return None
    
    result = f'[{call.value[0]} for {iterator} in {target}]'
    return (assignment, result)

# for to list comprehension transformation
def t_for_to_listc(source):
    red = rb.RedBaron(source)
    # print source lines before
    print(red)
    # query all for nodes
    for_nodes = red.find_all("ForNode")
    for for_node in for_nodes:
        result = _t_for_to_listc_change(for_node)
        # skip if no transformations can be applied
        if result is None: continue
        # apply transformation
        result[0].value = result[1]
        parent = for_node.parent
        parent.remove(for_node)
    print('-'*150)
    # print source lines after
    print(red)
    changed = red.dumps()  # this is the dump of the changed source code
    print('-'*150)
    print(changed)


# for to if list comprehension match
def _t_for_to_listc_if_match(for_node) -> bool:
    return match_node(for_node, for_to_listc_if)

# for to if list comprehension with if change
def _t_for_to_listc_if_change(for_node) -> tuple | None:
    if not _t_for_to_listc_if_match(for_node): return None
    # get nodes
    if_node = for_node.value.find('ifelseblock').value.find('if')
    atomtrailers = if_node.value.find('atomtrailers')
    l_name_nodes = atomtrailers.value.find_all('name')
    
    if l_name_nodes[1].name.value != 'append': return None  # TODO: match this in pattern
    
    list_name = l_name_nodes[0].name.value
    # last node to assign to 'list_name'
    assignment = get_last_node_before(for_node, list_name, node_is_assignment_to)
    # last node to mention 'list_name'
    lastmention = get_last_node_before(for_node, list_name, node_mentions)
    # type and value checks for assignment node
    if (assignment is None or assignment is not lastmention or not node_is_empty_list(assignment.value)):
        return None
    
    iterator, target = for_node.iterator, for_node.target
    test = if_node.test
    call = atomtrailers.value.find('call')

    # call arguments' length should be exactly one
    if not len(call.value) == 1:
        return None
    # call and test should both mention the iterator
    if not (node_mentions(test,iterator.value) and node_mentions(call,iterator.value)):
        return None
    
    result = f'[{call.value[0]} for {iterator} in {target} if {test}]'
    return (assignment, result)

# for to if list comprehension transformation
def t_for_to_listc_if(source):
    red = rb.RedBaron(source)
    # print source lines before
    print(red)
    # query all for nodes
    for_nodes = red.find_all("ForNode")
    for for_node in for_nodes:
        result = _t_for_to_listc_if_change(for_node)
        # skip if no transformations can be applied
        if result is None: continue
        # apply transformation
        result[0].value = result[1]
        parent = for_node.parent
        parent.remove(for_node)
    print('-'*150)
    # print source lines after
    print(red)
    changed = red.dumps()  # this is the dump of the changed source code
    print('-'*150)
    print(changed)
