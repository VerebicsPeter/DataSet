# Script to muck about with redbaron

import redbaron as rb

source = """
l = []
for i in range(1, 100):
    if True: l.append(i)
"""

red = rb.RedBaron(source)
print(red.help(deep=True))
#print("root node's parent:", red.parent) # None
#ifelseblock = red.find('IfelseblockNode')
#print(ifelseblock.help(deep=True))

assignment = red.find('AssignmentNode')
print(assignment)
print(assignment.target.name)
print(assignment.value)
print(type(assignment.value))

print(assignment.value.help(deep=True))
print('Value of the list:', assignment.value.list)