from redbaron import RedBaron

import transformations as t

source_for_to_list = """
l0 = []
for i in range(1, 5):
    l0.append(i * i)

if 1:
    l1 = []
    for i in range(1, 100):
        l1.append(i)
    print(l1)

    l2 = []
    for i in range(1, 100):
        l2.append(twice(i) ** 2)
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

source_for_to_numpy_sum = """
import numpy as np
l = [1, 2, 3, 4, 5]
sum = 0
for num in l:
    sum += num
"""

def test_for_to_list():
    red = RedBaron(source_for_to_list)
    transformation = t.ForNodeTransformation(
        ast=red, rule=t.ForToListComprehension())
    transformation.transform_nodes()

def test_for_to_list_if():
    red = RedBaron(source_for_to_list_if)
    transformation = t.ForNodeTransformation(
        ast=red, rule=t.ForToListComprehensionIf())
    transformation.transform_nodes()

def test_for_to_numpy_sum():
    red = RedBaron(source_for_to_numpy_sum)
    transformation = t.ForNodeTransformation(
        ast=red, rule=t.ForToNumpySum(red))
    transformation.transform_nodes()

if __name__ == "__main__":
    test_for_to_numpy_sum()
