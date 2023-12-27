# Script to muck about with ast

import ast

source = """
"""

root = ast.parse(source)

print(ast.dump(root, indent=3))
