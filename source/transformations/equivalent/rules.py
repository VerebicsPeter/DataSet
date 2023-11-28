# Implementations of rules

from abc import ABC, abstractmethod

from ast import AST, expr, stmt

import ast


class Rule(ABC):
    """ Abstract base class for transformation rules, such as `ForToListComprehension`, `ForToDictComprehension` ...
    """
    
    @abstractmethod
    def match(self, node: AST, *args, **kwargs) -> bool:
        """Returns whether `node` matches pattern.
        """
        pass
    
    @abstractmethod
    def change(self, node: AST, *args, **kwargs) -> object | None:
        """Returns the change object if possible, else returns `None`.
        """
        pass


class ForRule(Rule):

    @abstractmethod
    def match(self, node: AST) -> bool:
        pass

    def change(self, node: AST) -> dict | None:
        if self.match(node):
            target, iter = node.target, node.iter
            ifs = []
            statement = node.body[0]
            if isinstance(statement, ast.If):
                ifs = [statement.test]
                statement: stmt = statement.body[0]
            change = self.get_change(target, iter, ifs, statement)
            if change: return change
    
    @abstractmethod
    def get_change(self, target: expr, iter: expr, ifs: list[expr], statement: stmt)-> dict | None:
        pass


class ForToListComprehension(ForRule):
    
    def match(self, node: AST) -> bool:
        match node:
            case(
                ast.For(
                    target=ast.Name(), iter=_,
                    body=[
                        ast.Expr(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(),
                                attr='append',
                                ctx=ast.Load()),
                            args=_))
                        |
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
                        ],
                        orelse=[])
                    ],
                    orelse=[])
            ):
                return True
            case _:
                return False
    
    def get_change(self, target: expr, iter: expr, ifs: list[expr], statement: stmt) -> dict | None:
        args = statement.value.args
        name = statement.value.func.value
        
        # create the resulting list comprehension
        result = ast.ListComp(
            generators=[
                ast.comprehension(target=target,iter=iter,ifs=ifs,is_async=0)
            ],
            elt=args[0] #this is correct because append only takes one argument
        )
        
        return {"id": name.id, "check": self.check, "result": result}
    
    def check(self, node: AST, _id: str) -> bool:
        """Returns whether `node` assigns an empty list to a id of `_id`.
        """
        match node:
            case ast.Assign(
                targets=[ast.Name(id, ctx=ast.Store())], value=ast.List(elts=[], ctx=ast.Load())
            ):
                return id == _id
        return False


class ForToDictComprehension(ForRule):
    
    def match(self, node: AST) -> bool:
        match node:
            case(
                ast.For(
                    target=ast.Name(ctx=ast.Store()), iter=_,
                    body=[(
                        ast.Assign(
                        targets=[
                            ast.Subscript(
                                value=ast.Name(ctx=ast.Load()), slice=_,
                                ctx=ast.Store())],
                        value=_)
                        |
                        ast.If(
                        test=_,
                        body=[
                            ast.Assign(
                            targets=[
                                ast.Subscript(
                                value=ast.Name(ctx=ast.Load()), slice=_,
                                ctx=ast.Store())
                            ],
                            value=_)
                        ],
                        orelse=[])
                    )],
                    orelse=[])
            ):
                return True
            case _:
                return False
    
    def get_change(self, target: expr, iter: expr, ifs: list[expr], statement: stmt) -> dict | None:
        slice = statement.targets[0].slice
        value = statement.value
        name  = statement.targets[0].value
        
        result = ast.DictComp(
            generators=[
                ast.comprehension(target=target,iter=iter,ifs=ifs,is_async=0)
            ],
            key=slice, value=value    
        )
        
        return {"id": name.id, "check": self.check, "result": result}
    
    def check(self, node: AST, _id: str) -> bool:
        """Returns whether `node` assigns an empty dict to a id of `_id`.
        """
        match node:
            case ast.Assign(
                targets=[ast.Name(id, ctx=ast.Store())], value=ast.Dict(keys=[], values=[])
            ):
                return id == _id
        return False


class ForToNumpySum(Rule):

    def match(self, node) -> bool:
        pass

    def change(self, node) -> tuple | None:
        pass


class InvertIfOrElse(Rule):

    def match(self, node) -> bool:
        match node:
            case ast.If(
                test=_, body=[*_], orelse=[*_] as _orelse
            ):
                return len(_orelse) > 0
            case _:
                return False
    
    def change(self, node) -> dict | None:
        if not self.match(node): return None
        
        test = node.test
        body = node.body
        orelse = node.orelse
        
        result = ast.If(
            body=orelse, orelse=body,
            test=ast.UnaryOp(op=ast.Not(), operand=test)
        )
        
        return { "result": result }


class RemoveDoubleNegation(Rule):
    
    def match(self, node: AST) -> bool:
        match node:
            case ast.UnaryOp(
                op=ast.Not(),operand=ast.UnaryOp(op=ast.Not(),operand= _ )
            ):
                return True
            case _:
                return False
    
    def change(self, node: AST) -> dict | None:
        if not self.match(node): return None
        
        result = node.operand.operand
        
        return { "result": result }
