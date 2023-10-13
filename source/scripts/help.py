# Script to muck about with redbaron

import redbaron as rb

source = """
l = [1, 2]
for i in range(1, 100):
    if True: l.append(i)
my_list = [1, 2, 3, 4]
my_empty_list = []
"""

red = rb.RedBaron(source)
#print(red.help(deep=True))
#print("root node's parent:", red.parent) # None
#ifelseblock = red.find('IfelseblockNode')
#print(ifelseblock.help(deep=True))

assignment = red.find('AssignmentNode')
#print(assignment)

list_node = assignment.find('ListNode')
#print('listnode value and type:',list_node.value,type(list_node.value))
#print(list_node.value.help(deep=True))