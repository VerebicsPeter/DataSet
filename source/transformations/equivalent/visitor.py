import ast

from ast import AST, NodeVisitor, NodeTransformer


def add_parent_attribute(root: AST) -> None:
    for node in ast.walk(root):
        for child in ast.iter_child_nodes(node):
            child.parent = node


def match_for_if_append(node):
    match node:
        case ast.For(
            target=ast.Name(),
            body=[
                ast.If(
                test=_,
                body=[
                    ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=_,
                            attr='append',
                            ctx=ast.Load()),
                        args=_))
                ],
                orelse=[])
            ]
        ) as result:
            target = result.target
            iter   = result.iter
            test   = result.body[0].test
            lsid   = result.body[0].body[0].value.func.value
            arg    = result.body[0].body[0].value.args[0]
            # pattern to assign
            pattern = f'[{ast.unparse(arg)} for {ast.unparse(target)} in {ast.unparse(iter)} if {ast.unparse(test)}]'
            print()
            print(f'Matched pattern!')
            print()
            print("Target:")
            print(ast.dump(target))
            print("Iterator:")
            print(ast.dump(iter))
            print("Test:")
            print(ast.dump(test))
            print("List name:")
            print(ast.dump(lsid))
            print("Argument:")
            print(ast.dump(arg))
            print("Resulted pattern:")
            print(pattern)
            print()
            if isinstance(lsid, ast.Name): return (lsid.id, pattern)


class ForVisitor(NodeVisitor):
    
    # visits for nodes
    def visit_For(self, node: AST):
        print('-'*150)
        print(ast.dump(node, indent=2))
        print('-'*150)
        result = match_for_if_append(node)
        
        if result:
            print('-'*150)
            print("parent:", node.parent)
            print("listId:", result[0])
            if node.parent.body:
                parent_list = node.parent.body
                i = parent_list.index(node)
                if i > 0 and self.__node_assign__(parent_list[i-1], result[0]):
                    #print("!result apllicable!")
                    result_node = ast.parse(f'{result[0]} = {result[1]}')
                    parent_list[i-1] = result_node
                    # remove the for node
                    parent_list.remove(node)
            print('-'*150)
        print('\n')
        
        self.generic_visit(node)
    
    # matches empty list assignments
    def __node_assign__(self, node: AST, _id: str):
        match node:
            case ast.Assign(targets=[ast.Name(id, ctx=ast.Store())], value=ast.List(elts=[], ctx=ast.Load())):
                return id == _id
        return False


if __name__ == "__main__":
    
    source = """
kaka = []

for num in [1, 2, 3]:
    if even(num):
        l.append(num * 3)

print("Hello, World!")        

for i in range(1, 5):
    print(i)
""" 
    
    root = ast.parse(source)
    add_parent_attribute(root)
    
    visitor = ForVisitor()
    visitor.visit(root)
    
    print('-'*150)
    
    result = ast.unparse(root)
    print(result)
    print('-'*150)
    print(ast.dump(root, indent=2))
