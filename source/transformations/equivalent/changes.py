
import ast

from dataclasses import dataclass

@dataclass
class InPlace:
    changed: ast.AST

@dataclass
class ReduceFor:
    changed: ast.AST
    target: ast.Assign
    remove: ast.For


def deconstruct_for(node: ast.For):
        target = node.target
        iter = node.iter
        stmt = node.body[0]
        ifs = []
        if isinstance(stmt, ast.If):
            ifs.append(stmt.test)
            stmt = stmt.body[0]
        return (target, iter, stmt, ifs)


class Changers:
    
    @staticmethod
    def for_to_list_comp(_assign: ast.Assign, _for: ast.For):
        # get values from statement
        target, iter, stmt, ifs = deconstruct_for(_for)
        # NOTE: maybe put this in a try block
        args = stmt.value.args
        # create the resulting list comprehension
        result = ast.ListComp(
            elt=args[0],  # this is correct because append only takes one argument
            generators=[ast.comprehension(target=target,iter=iter,ifs=ifs,is_async=0)]
        )
        return ReduceFor(result, _assign, _for)
