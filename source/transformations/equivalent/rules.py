# Implementations of rules

# TODO: maybe move rules from here to their own transformation file

from abc import ABC, abstractmethod

from ast import AST

import ast


class Rule(ABC):
    """ Abstract base class for transformation rules, such as `ForToListComprehension`, `ForToDictComprehension` ...
    """
    
    @abstractmethod
    def match(self, *args, **kwargs) -> bool:
        pass
    
    @abstractmethod
    def change(self, *args, **kwargs) -> object | None:
        pass


class ForToListComprehension(Rule):
    
    def match(self, node: AST) -> bool:
        """Returns whether `node` matches the pattern.
        """
        match node:
            case(
                ast.For(
                    target=ast.Name(),
                    body=[
                        ast.Expr(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(),
                                attr='append',
                                ctx=ast.Load()),
                            args=_))]
            ) | ast.For(
                    target=ast.Name(),
                    body=[
                        ast.If(
                        test=_,
                        body=[
                            ast.Expr(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(),
                                    attr='append',
                                    ctx=ast.Load()),
                                args=_))
                        ],orelse=[])]
            )):
                return True
            case _:
                return False
    
    def change(self, node: AST) -> dict | None:
        """Returns the change if it is possible, else returns `None`.
        """
        if self.match(node):
            target, iter = node.target, node.iter
            
            ifs = []
            body = node.body[0]
            if isinstance(body, ast.If):
                ifs = [body.test]
                body = body.body[0]
            
            args = body.value.args
            name = body.value.func.value
            
            # create the resulting list comprehension
            result = ast.ListComp(
                generators=[
                    ast.comprehension(target=target,iter=iter,ifs=ifs,is_async=0)
                ],
                elt=args[0] #this is correct because append only takes one argument
            )
            
            return {"id": name.id, "check": self.check, "result": result}
    
    def check(self, node: AST, _id: str) -> bool:
        """Returns whether `node` assigns an empty list to a name-node with id of `_id`.
        """
        match node:
            case ast.Assign(
                targets=[ast.Name(id,      ctx=ast.Store())],
                value  = ast.List(elts=[], ctx=ast.Load())):
                return id == _id
        return False


class ForToDictComprehension(Rule):
    
    def match(self, node) -> bool:
        pass
    
    def change(self, node) -> tuple | None:
        pass

class ForToNumpySum(Rule):

    def match(self) -> bool:
        pass

    def change(self, node) -> tuple | None:
        pass
