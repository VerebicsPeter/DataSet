# Tests for equivalent transformations on for nodes

# TODO: assertions, proper tests

import ast

from ..equivalent.visitors import TFor

from ..equivalent.rules import (
    ForToListComprehension,
    ForToDictComprehension,
    ForToSetComprehension,
    ForToSum,
    ForToSumNumpy,
)

source_for_to_list = """
l = []
for i in iterable:
    l.append(f(i))
"""

source_for_to_list_if = """
l = []
for i in nums:
    if p(i):
        l.append(f(i))
"""

source_for_to_dict = """
d = {}
for i in iterable:
    d[f_1(i)] = f_2(i)
"""

source_for_to_dict_if = """
d = {}
for i in iterable:
    if p(i):
        d[f_1(i)] = f_2(i)
"""

source_for_to_set = """
l = set()
for i in iterable:
    l.add(f(i))
"""

source_for_to_set_if = """
l = set()
for i in nums:
    if p(i):
        l.add(f(i))
"""

source_for_to_sum = """
s = 0
for x in xs:
    s += f(x)
"""

source_for_to_sum_if = """
s = 0
for x in xs:
    if p(x):
        s += f(x)
"""


def print_unparse(node: ast.AST):
    print(ast.unparse(node))
    print('-'*100)

# run with:
# `python3 -m source.transformations.tests.testForNode`
if __name__ == "__main__":
    
    print('#'*100)
    print('\nTesting for to list comprehension:\n')    
    print('#'*100)
    TFor(ForToListComprehension()).transform_ast(tree:=ast.parse(source_for_to_list))
    print_unparse(tree)
    TFor(ForToListComprehension()).transform_ast(tree:=ast.parse(source_for_to_list_if))
    print_unparse(tree)
    
    print('#'*100)
    print('\nTesting for to dict comprehension:\n')
    print('#'*100)
    TFor(ForToDictComprehension()).transform_ast(tree:=ast.parse(source_for_to_dict))
    print_unparse(tree)
    TFor(ForToDictComprehension()).transform_ast(tree:=ast.parse(source_for_to_dict_if))
    print_unparse(tree)
    
    print('#'*100)
    print('\nTesting for to set comprehension:\n')
    print('#'*100)
    TFor(ForToSetComprehension()).transform_ast(tree:=ast.parse(source_for_to_set))
    print_unparse(tree)
    TFor(ForToSetComprehension()).transform_ast(tree:=ast.parse(source_for_to_set_if))
    print_unparse(tree)
    
    print('#'*100)
    print('\nTesting for to sum:\n')
    print('#'*100)
    TFor(ForToSum()).transform_ast(tree:=ast.parse(source_for_to_sum))
    print_unparse(tree)
    TFor(ForToSum()).transform_ast(tree:=ast.parse(source_for_to_sum_if))
    print_unparse(tree)
