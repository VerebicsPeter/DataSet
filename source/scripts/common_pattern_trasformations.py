# NOTE: Use `match ... case` for readability

import redbaron as rb

# Utility functions

def node_count_children(node, type: str) -> int:
    # return 0 on leaf
    if isinstance(node.value, str): return 0
    return len(node.value.find_all(type))

def node_mentions(node, name: str) -> bool:
    return len(node.find_all('name', value=name))

def node_is_assignment_to(node, name: str) -> bool:
    if isinstance(node, rb.AssignmentNode):
        return node.target.name.value == name
    return False

def get_last_node_before(node, name = None, predicate = lambda _node, _name: True):
    index = node.index_on_parent
    if index is None: return None
    last = None
    for x in node.parent[0:index]:
        if predicate(x, name): last = x
    return last

# Transformations:

def t_for_to_listcomprehension_match(for_node) -> bool:
    if node_count_children(for_node,'IfelseblockNode') != 1:
        return False
    if (node_count_children(for_node.value.find('IfelseblockNode'),'ElifNode') or
        node_count_children(for_node.value.find('IfelseblockNode'),'ElseNode')):
        return False
    if (node_count_children(
        for_node.
        value.find('IfelseblockNode').
        value.find('IfNode'),
        'AtomtrailersNode') != 1
        ):
        return False
    if (node_count_children(
        for_node.
        value.find('IfelseblockNode').
        value.find('IfNode').
        value.find('AtomtrailersNode'),
        'name') != 3):
        return False
    return True

def t_for_to_listcomprehension(for_node) -> tuple | None:
    if not t_for_to_listcomprehension_match(for_node): return None
    
    iterator, target = for_node.iterator, for_node.target

    # get nodes necessary for transformation
    if_node = for_node.value.find('IfelseblockNode').value.find('IfNode')
    # namenodes is the list of name nodes in the atom trailers node inside if node
    namenodes = if_node.value.find_all('name')
    # value check for name nodes
    if namenodes[1].name.value != 'append':
        return None
    if namenodes[2].name.value != iterator.name.value:
        return None
    name = namenodes[0].name.value

    assignment_node = get_last_node_before(for_node, name, node_is_assignment_to)
    last_mention    = get_last_node_before(for_node, name, node_mentions)
    # type and value checks for assignment node
    if assignment_node is None:
        return None
    if not isinstance(assignment_node.value, rb.ListNode):
        return None
    if len(assignment_node.list.value):
        return None
    if assignment_node is not last_mention:
        return None
    
    test = if_node.test
    result = f'[{iterator} for {iterator} in {target} if {test}]'
    return (assignment_node, result)

source = """
def even(x): return x % 2 == 0

result = []
for i in range(1, 5):
    if even(i): result.append(i)

if 2 % 2 == 0:
    
    l2 = []
    l2.append(42)
    for i in range(1, 100):
        if i % 5 == 0: l2.append(i)
    print(l2)
    
    l1 = []
    
    for i in range(1, 100):
        if i % 5 == 0: l1.append(i)
    print(l1)
else:
    importante = [1, 2, 3]
    for i in range(1, 100):
        if i % 5 == 0: importante.append(i)
    print('haha')

for i in range(1,3):
    if i == 2:
        print('fizz')
    else:
        print('buzz')

print(result)
"""

red = rb.RedBaron(source)
# print source code before
print(red)
# query all for nodes
for_nodes = red.find_all("ForNode")
for for_node in for_nodes:
    result = t_for_to_listcomprehension(for_node)
    if result is not None:
        result[0].value = result[1]
        parent = for_node.parent
        parent.remove(for_node)
print('-'*150)
# print source code after
print(red)