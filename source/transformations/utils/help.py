# Script to muck about with ast

import ast

source = """
sum = 0.0
"""

root = ast.parse(source)

print(ast.dump(root, indent=3))

print(type(root.body[0].targets[0].id))
