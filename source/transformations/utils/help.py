# Script to muck about with ast

import ast

rec = {}
#print(rec["_source"])
#print(rec["autopep+for_to_comp"])
exit(1)

root = ast.parse(source)

print(ast.dump(root, indent=3))