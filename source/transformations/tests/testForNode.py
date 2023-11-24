# Tests for equivalent transformations on for nodes

import ast

from transformations.equivalent.t_complex import ForNodeTransformation

from transformations.equivalent.visitors import ForTransformer

from transformations.equivalent.rules import (
    ForToListComprehension,
    ForToDictComprehension,
    ForToNumpySum
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

def print_result(t: ForNodeTransformation):
    print()
    print(ast.unparse(t.ast))
    print()

def test_for_to_list():
    print(source_for_to_list)
    root = ast.parse(source_for_to_list)
    t = ForNodeTransformation(ast=root)
    t.transform_nodes(ForTransformer(ForToListComprehension()))
    print_result(t)

def test_for_to_list_if():
    print(source_for_to_list_if)
    root = ast.parse(source_for_to_list_if)
    t = ForNodeTransformation(ast=root)
    t.transform_nodes(ForTransformer(ForToListComprehension()))
    print_result(t)

def test_for_to_dict():
    pass

def test_for_to_dict_if():
    pass

def test_for_to_numpy_sum():
    pass


if __name__ == "__main__":
    
    print('#'*150)
    print('\nTesting for to list comprehension:\n')    
    print('#'*150)
    test_for_to_list()
    
    print('#'*150)
    print('\nTesting for to list comprehension with if:\n')
    print('#'*150)
    test_for_to_list_if()
