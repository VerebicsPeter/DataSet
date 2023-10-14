# NOTE: Use 'match ... case' for readability

import redbaron as rb

from utils import node_count, get_last_node_before, node_mentions, node_is_assignment_to

# guard for transformation
def _t_for_to_listcomprehension_match(for_node) -> bool:
    if node_count(for_node,'IfelseblockNode') != 1:
        return False
    if (node_count(for_node.value.find('IfelseblockNode'),'ElifNode') or
        node_count(for_node.value.find('IfelseblockNode'),'ElseNode')):
        return False
    if (node_count(
        for_node.
        value.find('IfelseblockNode').
        value.find('IfNode'),
        'AtomtrailersNode') != 1
    ):
        return False
    if (node_count(
        for_node.
        value.find('IfelseblockNode').
        value.find('IfNode').
        value.find('AtomtrailersNode'),
        'name') < 3
    ):
        return False
    if (node_count(
        for_node.
        value.find('IfelseblockNode').
        value.find('IfNode').
        value.find('AtomtrailersNode'),
        'callnode') != 1
    ):
        return False
    return True

# for transformation
def _t_for_to_listcomprehension_change(for_node) -> tuple | None:
    if not _t_for_to_listcomprehension_match(for_node): return None
    if_node = for_node.value.find('ifelseblock').value.find('if')
    atomtrailers = if_node.value.find('atomtrailers')
    # namenodes is the list of name nodes in the atom trailers node inside if node
    namenodes = if_node.value.find_all('name')
    # second name in name nodes should be 'append'
    if namenodes[1].name.value != 'append': return None
    # first name in name nodes should be a name of a list
    name = namenodes[0].name.value
    # last node to assigm to 'name'
    assignment = get_last_node_before(for_node, name, node_is_assignment_to)
    # last node to mention 'name'
    lastmention = get_last_node_before(for_node, name, node_mentions)
    # type and value checks for assignment node
    if (assignment is None or
        assignment is not lastmention or
        not isinstance(assignment.value, rb.ListNode) or len(assignment.list.value)):
        return None
    iterator, target = for_node.iterator, for_node.target
    test = if_node.test
    call = atomtrailers.value.find('call')
    # call and test should both mention the iterator
    if not (node_mentions(test,iterator.value) and node_mentions(call,iterator.value)):
        return None
    # call argument length should be exactly one
    if len(call.value) > 1: return None
    result = f'[{call.value[0]} for {iterator} in {target} if {test}]'
    return (assignment, result)

def t_for_to_listcomprehension(source):
    red = rb.RedBaron(source)
    # print source code before
    print(red)
    # query all for nodes
    for_nodes = red.find_all("ForNode")
    for for_node in for_nodes:
        result = _t_for_to_listcomprehension_change(for_node)
        # skip if no transformations can be applied
        if result is None: continue
        # apply transformation
        result[0].value = result[1]
        parent = for_node.parent
        parent.remove(for_node)
    print('-'*150)
    # print source code after
    print(red)
    changed = red.dumps() # this is the dump of the changed source code
