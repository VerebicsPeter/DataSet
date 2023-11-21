# Tests for equivalent transformations on assignment nodes

from redbaron import RedBaron

from transformations.equivalent.tNodeSpecific import AssignmentNodeTransformation

from transformations.equivalent.rules import ElevateAssignment


source_elevate_assignment = """
a = [1, 2, 3]
a.append(4)
c = len(a)
print(a)
b = [42, 69]
print(b)
d = len(b)
"""


def do_transformation(t: AssignmentNodeTransformation):
    # print source lines before
    print(t.ast)
    print('-'*150)
    
    t.transform_nodes()

    # print source lines after
    print(t.ast)
    print('-'*150)
    
    # this is the dump of the changed source code
    changed = t.ast.dumps()
    print(changed)


def test_elevate_assignment():
    red = RedBaron(source_elevate_assignment)
    transformation = AssignmentNodeTransformation(
        ast=red,
        rule=ElevateAssignment()
    )
    do_transformation(transformation)
 
    
if __name__ == "__main__":
    
    print("\nTesting elevate assignment nodes:\n")
    test_elevate_assignment()
