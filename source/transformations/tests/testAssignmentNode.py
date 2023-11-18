# Tests for equivalent transformations on assignment nodes


from redbaron import RedBaron

from transformations.equivalent.tAssignmentNode import AssignmentNodeTransformation

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

def test_elevate_assignment():
    red = RedBaron(source_elevate_assignment)
    transformation = AssignmentNodeTransformation(
        ast=red,
        rule=ElevateAssignment()
    )
    transformation.transform_nodes()
    
if __name__ == "__main__":
    
    print("\nTesting elevate assignment nodes:\n")
    test_elevate_assignment()
