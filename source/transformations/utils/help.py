# Script to muck about with ast

import ast

import os

print(__file__)
print(os.path.join(os.path.abspath(__file__), '../../../'))

source = """
"""

root = ast.parse(source)

print(ast.dump(root, indent=3))

exit(1)