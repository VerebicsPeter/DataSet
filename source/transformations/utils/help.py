# Script to muck about with ast and redbaron

import redbaron as rb


def match_for_loop(node):
    match node:
        case rb.ForNode() as for_loop:
            return (
                len(for_loop.value) == 1 and
                match_if_else_block_conditions(for_loop.value[0]))
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


def match_if_else_block_conditions(node):
    match node:
        case rb.IfelseblockNode() as if_else_block:
            return (
                len(if_else_block.value) == 1 and
                match_if_block_conditions(if_else_block.value[0]))
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


source = """
newdict = {}
for x in range(10):
    newdict[x + 1] = x ** 3
"""

#red = rb.RedBaron(source),
#for_node = red.find('for')

print('-'*150)
