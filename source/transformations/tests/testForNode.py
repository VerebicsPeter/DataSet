# Tests for equivalent transformations on for nodes

# TODO: assertions, proper tests

# (run with `python3 -m source.transformations.tests.testForNode`)

import ast

from ..transformation import NodeTransformation

from ..equivalent.visitors import ForTransformer

from ..equivalent.rules import (
    ForToListComprehension,
    ForToDictComprehension,
    ForToSetComprehension,
    ForToSum,
    ForToSumNumpy,
)

source_for_to_list = """
l0 = []
for i in range(1, 5):
    l0.append(i * i)
print(l0)
l1 = []
for i in ['a', 'b', 'c']:
    l1.append(i)
print(l1)
"""

source_for_to_list_if = """
l0 = []
for i in nums:
    if even(i): l0.append(i * i)
print(l0)
l1 = []
for i in range(1, 100):
    if i % 5 == 0: l1.append(i)
print(l1)
"""

source_for_to_dict = """
newdict = {}
for x in range(10):
    newdict[x + 1] = x ** 3
"""

source_for_to_dict_if = """
newdict = {}
for x in range(10):
    if x % 2 == 0:
        newdict[x + 1] = x ** 3
"""

source_for_to_numpy_sum = """
import numpy as np
l = [1, 2, 3, 4, 5]
sum = 0
for num in l:
    sum += num
"""

def print_result(t: NodeTransformation):
    print()
    print(t.get_source())
    print()

def test_for_to_list():
    print(source_for_to_list)
    root = ast.parse(source_for_to_list)
    t = NodeTransformation(ast=root)
    t.transform_nodes(ForTransformer(ForToListComprehension()))
    print_result(t)

def test_for_to_list_if():
    print(source_for_to_list_if)
    root = ast.parse(source_for_to_list_if)
    t = NodeTransformation(ast=root)
    t.transform_nodes(ForTransformer(ForToListComprehension()))
    print_result(t)

def test_for_to_dict():
    print(source_for_to_dict)
    root = ast.parse(source_for_to_dict)
    t = NodeTransformation(ast=root)
    t.transform_nodes(ForTransformer(ForToDictComprehension()))
    print_result(t)

def test_for_to_dict_if():
    print(source_for_to_dict_if)
    root = ast.parse(source_for_to_dict_if)
    t = NodeTransformation(ast=root)
    t.transform_nodes(ForTransformer(ForToDictComprehension()))
    print_result(t)

def test_for_to_numpy_sum():
    # TODO
    pass


if __name__ == "__main__":
    
    print('#'*100)
    print('\nTesting for to list comprehension:\n')    
    print('#'*100)
    test_for_to_list()
    
    print('#'*100)
    print('\nTesting for to list comprehension with if:\n')
    print('#'*100)
    test_for_to_list_if()
    
    
    print('#'*100)
    print('\nTesting for to dict comprehension:\n')    
    print('#'*100)
    test_for_to_dict()
    
    
    print('#'*100)
    print('\nTesting for to dict comprehension if:\n')    
    print('#'*100)
    test_for_to_dict_if()
