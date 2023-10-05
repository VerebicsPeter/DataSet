from redbaron import RedBaron

source = """
def even(x): return x % 2 == 0
result = []
for i in range(5):
    if even(i): result.append(i)
"""
red = RedBaron(source)

print(red)
print(red.dumps())

for_nodes = red.find_all("ForNode")

print('For nodes found:')
for node in for_nodes:
    print(node)