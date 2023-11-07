# Implementations of code transformations
# NOTE: Use 'match ... case' for readability
# TODO: transformation function that takes multiple nodes as parameters
# TODO: typing and callable
# TODO: Tamásnak írni a csoportban a githubos cuccal kapcsolatban

import redbaron as rb

from utils import match_node, node_mentions, node_is_assignment_to, node_is_empty_list, get_last_node_before
from patterns import for_to_listc, for_to_listc_if, for_to_numpy_sum


def transform_for_nodes(ast, match, change, params: dict | None = None):
    # print source lines before
    print(ast)
    print('-'*150)
    
    for_nodes = ast.find_all('for')
    
    for for_node in for_nodes:
        # skip if node doesn't match
        if not match(for_node): continue
        
        result = None
        # get change
        if params is None:
            result = change(for_node)
        else:
            result = change(for_node, params)
        
        # skip if change can't be applied
        if result is None: continue
        # apply the change
        result[0].value = result[1]
        # unlink the for node
        parent = for_node.parent
        parent.remove(for_node)
    
    # print source lines after
    print(ast)
    changed = ast.dumps()  # this is the dump of the changed source code
    print('-'*150)
    print(changed)


def get_module_import(ast, module_name: str):
    import_node = ast.find_all('import').find('name', value=module_name)
    
    match import_node:
        case None:
            return None
    match import_node.parent:
        case rb.DottedAsNameNode():
            return import_node.parent.target
        case _:
            return module_name


# for to list comprehension match
def _t_for_to_listc_match(for_node) -> bool:
    return match_node(for_node, for_to_listc)

# for to list comprehension change
def _t_for_to_listc_change(for_node) -> tuple | None:
    # get nodes
    atomtrailers = for_node.value.find('atomtrailers')
    l_name_nodes = atomtrailers.value.find_all('name')
    
    list_name = l_name_nodes[0].name.value

    lastvassign = get_last_node_before(for_node, list_name, node_is_assignment_to)
    lastmention = get_last_node_before(for_node, list_name, node_mentions)

    if (lastvassign is None or lastvassign is not lastmention or not node_is_empty_list(lastvassign.value)):
        return None
    
    iterator, target = for_node.iterator, for_node.target
    call = atomtrailers.value.find('call')

    if not len(call.value) == 1:
        return None
    if not node_mentions(call, iterator.value):
        return None
    
    result = f'[{call.value[0]} for {iterator} in {target}]'
    return (lastvassign, result)

# for to list comprehension transformation
def t_for_to_listc(source):
    red = rb.RedBaron(source)
    transform_for_nodes(red, _t_for_to_listc_match, _t_for_to_listc_change)


# for to if list comprehension match
def _t_for_to_listc_if_match(for_node) -> bool:
    return match_node(for_node, for_to_listc_if)

# for to if list comprehension with if change
def _t_for_to_listc_if_change(for_node) -> tuple | None:
    # get nodes
    if_node = for_node.value.find('ifelseblock').value.find('if')
    atomtrailers = if_node.value.find('atomtrailers')
    l_name_nodes = atomtrailers.value.find_all('name')
    
    list_name = l_name_nodes[0].name.value
    # last node to assign to 'list_name'
    lastvassing = get_last_node_before(for_node, list_name, node_is_assignment_to)
    # last node to mention 'list_name'
    lastmention = get_last_node_before(for_node, list_name, node_mentions)
    # type and value checks for assignment node
    if (lastvassing is None or lastvassing is not lastmention or not node_is_empty_list(lastvassing.value)):
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
    return (lastvassing, result)

# for to if list comprehension transformation
def t_for_to_listc_if(source):
    red = rb.RedBaron(source)
    transform_for_nodes(red, _t_for_to_listc_if_match, _t_for_to_listc_if_change)


# for to numpy sum match
def _t_for_to_numpy_sum_match(for_node):
    return match_node(for_node, for_to_numpy_sum)

# for to numpy sum change
def _t_for_to_numpy_sum_change(for_node, params):
    # get nodes
    for_assignment = for_node.value.find('assignment')
    # inc variable's name
    inc_name = for_assignment.value.find('name')
    # sum variable's name
    sum_name = for_assignment.target.value
    # assignment is the initial assignment to sum variable
    lastvassign = get_last_node_before(for_node, sum_name, node_is_assignment_to)
    lastmention = get_last_node_before(for_node, sum_name, node_mentions)
    
    if (lastvassign is None or lastvassign is not lastmention):
        return None
    
    if not (isinstance(lastvassign.value, rb.IntNode) and lastvassign.value.value == '0'):
        return None
    
    iterator, target = for_node.iterator, for_node.target

    match iterator:
        case rb.NameNode() as name:
            if name.value != inc_name.value: return None

    target_lasmention = get_last_node_before(lastvassign, target.value, node_mentions)
    # if target is not in scope return None
    if target_lasmention is None:
        return None

    result = f"{params['numpy']}.sum({target})"
    return (lastvassign, result)

# for to numpy sum transformation
def t_for_to_numpy_sum(source):
    red = rb.RedBaron(source)
    
    numpy_name = get_module_import(red, 'numpy')
    if numpy_name is None: return None
    
    transform_for_nodes(red, _t_for_to_numpy_sum_match, _t_for_to_numpy_sum_change, params={'numpy': numpy_name})
