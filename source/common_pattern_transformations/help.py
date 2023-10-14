# Script to muck about with ast and redbaron

#import ast
import redbaron as rb

def match_for_pattern(node):
    match node:
        case rb.ForNode(
            iterator = rb.NameNode(value = 'i')
        ):
            return True
        case None:
            return False
        case _:
            return False

def match_list_pattern(node):
    match node:
        case rb.ListNode():
            return True
        case _:
            return False

source0 ="""
l = []
for k in range(1, 100):
    if True: l.append(k)
"""

source1 = """
if 2: pass
l = [1, 2, 3]
for i in range(1, 100):
    if True: l.append(i)
for k in range(1, 100):
    if True: l.append(k)
my_list = [1, 2, 3, 4]
my_empty_list = []
"""

source2="""
x = 42
exp0 = x
exp1 = x ** 2
exp2 = x ** 3 + i ** 2 + x
exp3 = type(x)
"""

def node_mentions(node, name: str) -> bool:
    return len(node.find_all('name', value=name))

red = rb.RedBaron(source0)
print(type(red))
for node in red.find_all('ForNode'):
    print(node)
    print(node.help())