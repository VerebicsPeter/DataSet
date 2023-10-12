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

def node_get_last_by_name(node, name: str, predicate = lambda x, y: True):
    index = node.index_on_parent
    if index is None: return None
    last = None
    for x in node.parent[0:index]:
        if predicate(x, name): last = x
    return last

# Transformations:

def t_for_to_listcomprehension(for_node) -> tuple | None:
    iterator, target = for_node.iterator, for_node.target

    if node_count_children(for_node,'IfelseblockNode') != 1:
        return None
    if_else_block = for_node.value.find('IfelseblockNode')

    if node_count_children(if_else_block,'ElseNode'):
        return None
    if_node = if_else_block.value.find('IfNode')

    if node_count_children(if_node,'AtomtrailersNode') != 1:
        return None
    atom_trailers_node = if_node.value.find('AtomtrailersNode')

    if node_count_children(atom_trailers_node,'name') != 3:
        return None
    namenodes = if_node.value.find_all('name')

    test = if_node.test
    name = namenodes[0].name.value
    assignment_node = node_get_last_by_name(for_node, name, node_is_assignment_to)
    
    if assignment_node is None:
        return None
    if not isinstance(assignment_node.value, rb.ListNode):
        return None
    if len(assignment_node.list.value):
        return None

    last_mention = node_get_last_by_name(for_node, name, node_mentions)

    if assignment_node is not last_mention:
        return None
    if namenodes[1].name.value != 'append':
        return None
    if namenodes[2].name.value != iterator.name.value:
        return None

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
