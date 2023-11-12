from redbaron import RedBaron

from transformations import ForNodeTransformation

from rules import (
    ForToListComprehension,
    ForToListComprehensionIf,
    ForToDictComprehension,
    ForToDictComprehensionIf,
    ForToNumpySum
)


source_for_to_list = """
l0 = []
for i in range(1, 5):
    l0.append(i * i)

if 1:
    num_dict = {"a": 1, "b": 2, "c": 3}
    
    l1 = []
    for i in ['a', 'b', 'c']:
        l1.append(i)
    print(l1)
    
    l2 = []
    for i in num_dict:
        l2.append(twice(num_dict[i]) ** 2)
    print(l2)
    
if 2:
    l3 = [1, 2, 3]
    for i in range(1, 100):
        l3.append(i)
"""

source_for_to_list_if = """
def even(x): return x % 2 == 0
def twice(x): return 2 * x

l0 = []
for i in range(1, 5):
    if even(i): l0.append(i * i)

if 1:
    l1 = []
    for i in range(1, 100):
        if i % 5 == 0: l1.append(i)
    print(l1)

    l2 = []
    for i in range(1, 100):
        if even(i): l2.append(twice(i) ** 2)
    print(l2)
    
if 2:
    l3 = [1, 2, 3]
    for i in range(1, 100):
        if i % 5 == 0: l3.append(i)
"""

source_for_to_dict ="""
newdict = {}
for x in range(10):
    newdict[x + 1] = x ** 3
"""

source_for_to_dict_if ="""
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


def test_for_to_list():
    red = RedBaron(source_for_to_list)
    transformation = ForNodeTransformation(
        ast = red,
        rule = ForToListComprehension()
    )
    transformation.transform_nodes()


def test_for_to_list_if():
    red = RedBaron(source_for_to_list_if)
    transformation = ForNodeTransformation(
        ast = red,
        rule = ForToListComprehensionIf()
    )
    transformation.transform_nodes()


def test_for_to_dict():
    red = RedBaron(source_for_to_dict)
    transformation = ForNodeTransformation(
        ast = red,
        rule = ForToDictComprehension()
    )
    transformation.transform_nodes()
    

def test_for_to_dict_if():
    red = RedBaron(source_for_to_dict_if)
    transformation = ForNodeTransformation(
        ast = red,
        rule = ForToDictComprehensionIf()
    )
    transformation.transform_nodes()


def test_for_to_numpy_sum():
    red = RedBaron(source_for_to_numpy_sum)
    transformation = ForNodeTransformation(
        ast = red, 
        rule = ForToNumpySum(red)
    )
    transformation.transform_nodes()


if __name__ == "__main__":
    test_for_to_dict_if()
