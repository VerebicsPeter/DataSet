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
            ): return True
        return False
    
    def get_change(self, target: expr, iter: expr, ifs: list[expr], statement: stmt) -> dict | None:
        args = statement.value.args
        name = statement.value.func.value
        
        # create the resulting list comprehension
        result = ast.ListComp(
            elt=args[0], # this is correct because append only takes one argument
            generators=[
                ast.comprehension(target=target,iter=iter,ifs=ifs,is_async=0)
            ]
        )
        return {"id": name.id, "check": self.check, "result": result}
    
    def check(self, node: AST, _id: str) -> bool:
        """Returns whether `node` assigns an empty list to `_id`.
        """
        match node:
            case ast.Assign(
                targets=[ast.Name(id, ctx=ast.Store())], value=ast.List(elts=[], ctx=ast.Load())
            ): return id == _id
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
            ): return True
        return False
    
    def get_change(self, target: expr, iter: expr, ifs: list[expr], statement: stmt) -> dict | None:
        slice = statement.targets[0].slice
        value = statement.value
        name  = statement.targets[0].value
        # create resulting dict comprehension
        result = ast.DictComp(
            key=slice, value=value,  
            generators=[
                ast.comprehension(target=target,iter=iter,ifs=ifs,is_async=0)
            ]
        )
        return { "id": name.id, "check": self.check, "result": result }
    
    def check(self, node: AST, _id: str) -> bool:
        """Returns whether `node` assigns an empty dict to `_id`.
        """
        match node:
            case ast.Assign(
                targets=[ast.Name(id, ctx=ast.Store())], value=ast.Dict(keys=[], values=[])
            ): return id == _id
        return False


class ForToSum(ForRule):
    
    def match(self, node: AST):
        match node:
            case (
            ast.For(
                target=_, iter=_,
                body=[(
                    ast.AugAssign(
                        target=ast.Name(ctx=ast.Store()),
                        op=ast.Add(),value=_
                    )
                    |
                    ast.If(
                    test=_,
                    body=[
                        ast.AugAssign(
                            target=ast.Name(ctx=ast.Store()),
                            op=ast.Add(),value=_
                    )],
                    orelse=[])                    
                )],
                orelse=[])
            ): return True
        return False

    def get_change(self, target: expr, iter: expr, ifs: list[expr], statement: stmt) -> dict | None:
        inc = statement.value
        name = statement.target
        # create resulting sum call
        result = ast.Call(
            func=ast.Name(id='sum', ctx=ast.Load()),
            args=[
               ast.GeneratorExp(
                    elt=inc,
                    generators=[
                        ast.comprehension(target=target,iter=iter,ifs=ifs,is_async=0)
                    ]
                )],
            keywords=[]
        )
        return { "id": name.id, "check": self.check, "result": result }
    
    def check(self, node: AST, _id: str) -> bool:
        """Returns whether `node` assigns the literal 0 or 0.0 to `_id`.
        """
        match node:
            case ast.Assign(
                targets=[ast.Name(id, ctx=ast.Store())],
                value=(ast.Constant(0) | ast.Constant(0.0))
            ): return id == _id
        return False


class ForToSumNumpy(Rule):

    def match(self, node) -> bool:
        pass

    def change(self, node) -> tuple | None:
        pass


class InvertIf(Rule):

    def match(self, node: AST) -> bool:
        match node:
            case ast.If(
                test=_, body=[*_], orelse=[*_] as _orelse_
            ):
                return len(_orelse_) > 0
            case _:
                return False
    
    def change(self, node: AST) -> dict | None:
        if not self.match(node): return None
        
        test = node.test
        body = node.body
        orelse = node.orelse
        
        result = ast.If(
            body=orelse, orelse=body,
            test=ast.UnaryOp(op=ast.Not(), operand=test)
        )
        return { "result": result }


class ExtractFunctionDefGuard(Rule):
    
    def match(self, node: AST):
        match node:
            case(
                ast.FunctionDef(
                    name=_,
                    args=_,
                    body=[
                        ast.If(
                            test=_,
                            body=_,
                            orelse=[ast.Return(value=_)])
                    ],
                    decorator_list=_)
            ):
                return True
            case _:
                return False
    
    def change(self, node: AST) -> dict | None:
        if not self.match(node): return None
        
        f_name = node.name
        f_args = node.args
        f_decorator_list = node.decorator_list
        f_if = node.body[0]
        f_body = f_if.body
        f_guard_test = f_if.test
        f_guard_body = f_if.orelse
        
        guard = ast.If(
            test=ast.UnaryOp(op=ast.Not(),operand=f_guard_test),body=f_guard_body,
            orelse=[]
        )
        
        f_body.insert(0, guard)
        
        result = ast.FunctionDef(
            name=f_name,
            args=f_args,
            body=f_body,
            decorator_list=f_decorator_list,
        )
        
        return { "result": result }


class DoubleNegation(Rule):
    
    def match(self, node: AST) -> bool:
        match node:
            case ast.UnaryOp(
                op=ast.Not(),
                operand=ast.UnaryOp(
                    op=ast.Not(),
                    operand= _
                )
            ):
                return True
            case _:
                return False
    
    def change(self, node: AST) -> dict | None:
        if not self.match(node): return None
        
        result = node.operand.operand
        
        return { "result": result }


class DeMorgan(Rule):
    
    def match(self, node: AST) -> bool:
        match node:
            case ast.UnaryOp(
                op=ast.Not(),
                operand=ast.BoolOp(
                    op=ast.And() | ast.Or(),
                    values=_
                )
            ):
                return True
            case _:
                return False
    
    def change(self, node: AST) -> dict | None:
        if not self.match(node): return None
        
        values = [ ast.UnaryOp(op=ast.Not(), operand=value)
                                    for value in node.operand.values ]
        
        if isinstance(node.operand.op, ast.And):
            result = ast.BoolOp(
                op=ast.Or(),
                values=values
            )
            return { "result": result }
        
        if isinstance(node.operand.op, ast.Or):
            result = ast.BoolOp(
                op=ast.And(),
                values=values
            )
            return { "result": result }
        
        return None
