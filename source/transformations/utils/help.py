# Script to muck about with ast and redbaron

import ast

source = """
data = {}
data2 = { i : i+1 for i in l }
"""

root = ast.parse(source)

print(ast.dump(root, indent=3))
