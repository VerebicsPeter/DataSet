import transformations as t

source = """
def even(x): return x % 2 == 0

result = []
for i in range(1, 5):
    if even(i): result.append(i * i)

if 2 - 2 == 0:
    l1 = []
    l1.append(42)
    for i in range(1, 100):
        if i % 5 == 0: l2.append(i)
    print(l1)
    
    l2 = []
    for i in range(1, 100):
        if i % 5 == 0: l2.append(i)
    print(l2)

    l3 = []
    for i in range(1, 100):
        if even(i): l3.append(i ** 2)
        # this is a comment xd
    print(l3)

if 3 - 3 == 0:
    importante = [1, 2, 3]
    for i in range(1, 100):
        if i % 5 == 0: importante.append(i)
    print('haha')

if 4 - 4 == 0:
    l = []
    for i in range(1, 5):
        l.append(i)

for i in range(1,3):
    if i == 2:
        print('fizz')
    else:
        print('buzz')

print(result)
"""

t.t_for_to_listcomprehension(source)
