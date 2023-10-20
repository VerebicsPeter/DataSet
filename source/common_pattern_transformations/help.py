# Script to muck about with ast and redbaron

import redbaron as rb

import utils, patterns

def match_for_loop(node):
    match node:
        case rb.ForNode() as for_loop:
            return (
                len(for_loop.value) == 1 and
                match_if_else_block_conditions(for_loop.value[0]))
        case _:
            return False

def match_if_else_block_conditions(node):
    match node:
        case rb.IfelseblockNode() as if_else_block:
            return (
                len(if_else_block.value) == 1 and
                match_if_block_conditions(if_else_block.value[0]))
        case _: 
            return False

def match_if_block_conditions(node):
    match node:
        case rb.IfNode() as if_block:
            return (
                len(if_block.value) == 1 and
                match_atomtrailers_conditions(if_block.value[0]))
        case _:
            return False

def match_atomtrailers_conditions(node):
    match node:
        case rb.AtomtrailersNode() as atomtrailers:
            namenodes = atomtrailers.find_all('name')
            callnodes = atomtrailers.find_all('call')
            return (
                len(namenodes) == 3 and len(callnodes) == 1)
        case _:
            return False

source0="""
l = []
for i in range(1, 100):
    if True: l.append(i)
for i in range(1, 100):
    if True: print(i)
for i in range(1, 100):
    if True: l.append(i)
    elif i % 4 == 0: l.append(i**2)
    elif i % 5 == 0: l.append(i**3)
for i in range(1, 5):
    print('Hello, World!')
    print('Szeretem a levest!')
    if True == True: pass
for i in range(1, 100):
    if True: l.append(i)
    for j in range(1, 100):
        if True: l.append(j)
        for k in range(1, 100):
            if True: l.append(k)
"""

source1 = """
import numpy as np
l = [1, 2, 3, 4, 5]
sum = 0
for num in l:
    sum += num
"""

red = rb.RedBaron(source1)

print(red.help(deep = True))

exit(1)

for node in red.find_all('ForNode'):
    if utils.match_node(node, patterns.for_sum):  #(match_for_loop(node)):
        print('-'*55)
        print(node)
        print('-'*55)
        print(node.value.help())
