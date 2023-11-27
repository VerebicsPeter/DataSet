# Script to muck about with ast

import ast

source = """
if not (a and b):
    x
elif b:
    y
else:
    z
"""

root = ast.parse(source)

print(ast.dump(root, indent=3))
