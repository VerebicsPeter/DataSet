# Implementations of rules

    # TODO: try match two neighbouring nodes in a single pattern
    # TODO: try to make rules bidirectional

from typing import Callable

from abc import ABC, abstractmethod

from ast import AST, expr, stmt

import ast

import logging

from .changes import ReduceFor, InPlace, Changers

from .patterns import Patterns

from ..utils.helpers import Node


class Rule(ABC):
    """ Abstract base class for transformation rules
    """
    
    @abstractmethod
    def match(self, node: AST, *args, **kwargs) -> object | None:
        """Patterns matches on `node` parameter
        """
        pass
    
    @abstractmethod
    def change(self, node: AST, *args, **kwargs) -> object | None:
        """Returns the changes available on `node`
        """
        pass


class ForRule2(Rule):
    def __init__(self, pattern_Assign: Callable, pattern_For: Callable, changer: Callable) -> None:
        
        self.matcher_Assign : Callable[[AST]     , ast.Assign] = pattern_Assign
        self.matcher_For    : Callable[[AST, str], ast.For   ] = pattern_For
        
        self.matches: list[tuple[ast.Assign, ast.For]] = []
        
        self.changer: Callable[ [ast.Assign, ast.For], ReduceFor] = changer


    def match(self, node: AST):
        self.matches.clear()
        
        match node:
            case AST(body=[_,_,*_] as body):
                for a, f in zip(body, body[1:]):
                    m_a = self.matcher_Assign(a)
                    if not m_a:
                        continue
                    m_f = self.matcher_For(f, m_a.targets[0].id)
                    if not m_f:
                        continue
                    self.matches.append((m_a, m_f))
            case _:
                return


    def change(self, node: AST):
        self.match(node)
        return [self.changer(a,f) for a,f in self.matches]


class ForRuleMaker:
    def for_to_list_comp():
        return ForRule2\
        (
            Patterns.assign_empty_list,
            Patterns.for_to_list_comp,
            Changers.for_to_list_comp
        )


class ForRule(Rule):
    """Reduces a "sum based" for loop (Pattern) to a comprehensions (Result).
    """

    def match(self, node: AST) -> bool:
        # reset the state
        self._reset_state()

        try:
            p = node.parent.body
            i = node.parent.body.index(node)
        except Exception as e:
            logging.info(f"'ForRule.match' matching nodes parent: {e}")
            return False
        
        if i >= len(p) - 1:  # Make sure that the node is not the last in the scope
            return False

        self._Assign = self._match_Assign(node)
        
        if not self._Assign:
            return False
        
        logging.info("assignment matched pattern...")
        
        try:
            self._sum = self._Assign.targets[0].id  # sum ("sum name") is the id of
                                                    # the target in the assignment
            self._For = self._match_For(p[i+1], self._sum)
        except Exception as e:
            logging.info(f"'ForRule.match' matching for-node: {e}")
            return False
        
        logging.info(f"matched for node: {self._For}")
        
        return bool(self._For)
    

    def change(self, node: AST) -> ReduceFor | None:
        if self.match(node):
            target = self._For.target
            iter   = self._For.iter
            
            ifs,statement = [], self._For.body[0]
            if isinstance(statement, ast.If):
                ifs       =[statement.test]
                statement = statement.body[0]
            
            change = self._get_change(target, iter, ifs, statement)
            if change: return change

    @abstractmethod
    def _match_Assign(self, node: AST) -> AST | None:
        pass
    
    @abstractmethod
    def _match_For(self, node: AST, sum_id: str) -> AST | None:
        pass
    
    @abstractmethod
    def _get_change(self, target: expr, iter: expr, ifs: list[expr], statement: stmt) -> ReduceFor | None:
        pass
    
    def _reset_state(self) -> None:
        self._Assign : ast.Assign = None
        self._For    : ast.For    = None
        self._sum    : str        = None


class ForToListComprehension(ForRule):
    
    def _match_Assign(self, node: AST) -> AST | None:
        return Patterns.assign_empty_list(node)
    
    def _match_For(self, node: AST, sum_name: str) -> AST | None:
        return Patterns.for_to_list_comp(node, sum_name)
    
    def _get_change(self, target: expr, iter: expr, ifs: list[expr], statement: stmt) -> ReduceFor | None:
        if not self._Assign or not self._For: return None
        # get values from statement
        args = statement.value.args
        # create the resulting list comprehension
        result = ast.ListComp(
            elt=args[0],  # this is correct because append only takes one argument
            generators=[ast.comprehension(target=target,iter=iter,ifs=ifs,is_async=0)]
        )
        return ReduceFor(self._Assign, self._For, result)


class ForToDictComprehension(ForRule):
    
    def _match_Assign(self, node: AST) -> AST | None:
        match node:
            case( 
                ast.Assign(
                    targets=[ast.Name(ctx=ast.Store())],
                    value=ast.Dict(keys=[], values=[]))
                ):
                return node
        return None
    
    def _match_For(self, node: AST, sum_name: str) -> AST | None:
        match node:
            case(
                ast.For(
                target=ast.Name(ctx=ast.Store()),
                body=[
                    ast.Assign(
                    targets=[
                        ast.Subscript(
                            value=ast.Name(id=_ as _sum_name),
                            slice=_,
                            ctx=ast.Store())
                    ],
                    value=_)
                    |
                    ast.If(
                    test=_,
                    body=[
                        ast.Assign(
                        targets=[
                            ast.Subscript(
                                value=ast.Name(id=_ as _sum_name),
                                slice=_,
                                ctx=ast.Store())
                        ],
                        value=_)
                    ],
                    orelse=[]) as _body
                ],
                orelse=[])
                ):
                if len(Node.all_names(_body, sum_name)) - 1: return None
                return node if sum_name == _sum_name else None
        return None
    
    def _get_change(self, target: expr, iter: expr, ifs: list[expr], statement: stmt) -> ReduceFor | None:
        if not self._Assign or not self._For: return None
        # get values from statement
        slice = statement.targets[0].slice
        value = statement.value
        # create resulting dict comprehension
        result = ast.DictComp(
            key=slice, value=value,
            generators=[ast.comprehension(target=target,iter=iter,ifs=ifs,is_async=0)]
        )
        return ReduceFor(self._Assign, self._For, result)


class ForToSetComprehension(ForRule):

    def _match_Assign(self, node: AST) -> AST | None:
        """Returns whether `node` assigns an empty set"""
        match node:
            case( 
                ast.Assign(
                    targets=[ast.Name(ctx=ast.Store())],
                    value=ast.Call(func=ast.Name('set', ctx=ast.Load()), args=[], keywords=[]))
                ):
                return node
        return None

    def _match_For(self, node: AST, sum_name: str) -> AST | None:
        match node:
            case(
                ast.For(
                target=ast.Name(),
                body=[
                    ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=_ as _sum_name),
                            attr='add',
                            ctx=ast.Load()),
                        args=_))
                    |
                    ast.If(
                    test=_,
                    body=[
                        ast.Expr(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id=_ as _sum_name),
                                attr='add',
                                ctx=ast.Load()),
                            args=_))
                    ],
                    orelse=[]) as _body
                ],
                orelse=[])
                ):
                if len(Node.all_names(_body, sum_name)) - 1: return None
                return node if sum_name == _sum_name else None
        return None
    
    def _get_change(self, target: expr, iter: expr, ifs: list[expr], statement: stmt) -> dict | None:
        if not self._Assign or not self._For: return None
        # get values from statement
        args = statement.value.args
        # create the resulting set comprehension
        result = ast.SetComp(
            elt=args[0],  # this is correct because add only takes one argument
            generators=[ast.comprehension(target=target,iter=iter,ifs=ifs,is_async=0)]
        )
        return ReduceFor(self._Assign, self._For, result)


class ForToSum(ForRule):
    
    def _match_Assign(self, node: AST) -> AST | None:
        """Returns whether `node` assigns the literal 0 or 0.0"""
        match node:
            case(
                ast.Assign(
                    targets=[ast.Name(ctx=ast.Store())],
                    value=(ast.Constant(0) | ast.Constant(0.0)))
                ):
                return node
        return None
    
    def _match_For(self, node: AST, sum_name: str) -> AST | None:
        match node:
            case(
                ast.For(
                target=_,
                body=[
                    ast.AugAssign(
                        target=ast.Name(id=_ as _sum_name),
                        op=ast.Add(),
                        value=_)
                    |
                    ast.If(
                    test=_,
                    body=[
                        ast.AugAssign(
                            target=ast.Name(id=_ as _sum_name),
                            op=ast.Add(),
                            value=_)
                    ],
                    orelse=[]) as _body
                ],
                orelse=[])
                ):
                if len(Node.all_names(_body, sum_name)) - 1:
                    return None
                return node if sum_name == _sum_name else None
        return None

    def _get_change(self, target: expr, iter: expr, ifs: list[expr], statement: stmt) -> dict | None:
        if not self._Assign or not self._For: return None
        # get values from statement
        inc = statement.value
        # create resulting sum call
        result = ast.Call(
            func=ast.Name(id='sum', ctx=ast.Load()),
            args=[
               ast.GeneratorExp(
                    elt=inc,
                    generators=[ast.comprehension(target=target,iter=iter,ifs=ifs,is_async=0)]
                )],
            keywords=[]
        )
        return ReduceFor(self._Assign, self._For, result)


# TODO: implement
class ForToSumNumpy(ForRule):

    def match(self, node) -> bool:
        pass

    def change(self, node) -> dict | None:
        pass


class InvertIf(Rule):

    def match(self, node: AST) -> bool:
        match node:
            case ast.If(test=_, body=[*_], orelse=[*_] as _orelse_):
                # return False if the orelse is empty
                return len(_orelse_) > 0
            case _:
                return False
    
    def change(self, node: AST) -> InPlace | None:
        if not self.match(node): return None
        
        test = node.test
        body = node.body
        orelse = node.orelse
        
        result = ast.If(
            body=orelse, orelse=body, test=ast.UnaryOp(op=ast.Not(), operand=test)
        )
        return InPlace(result)


class GuardDef(Rule):
    
    def match(self, node: AST) -> tuple | None:
        match node:
            case(
                ast.FunctionDef(
                    name=_ as _name,
                    args=_ as _args,
                    body=[
                        ast.If(
                            test=_ as _test,
                            body=_ as _body,
                            orelse=[ast.Return(value=_)] as _orelse)
                    ],
                    decorator_list=_ as _decorator_list)
                ):
                return (_name, _args, _test, _body, _orelse, _decorator_list)
            case _:
                return None
    
    def change(self, node: AST) -> InPlace | None:
        if not (matched := self.match(node)): return None
        (
            f_name,
            f_args,
            f_test,    # guarding if's test
            f_body,    # function's body
            f_orelse,  # guarding if's body
            f_decorator_list,
        ) = matched
        
        guard = ast.If(
            test=ast.UnaryOp(op=ast.Not(), operand=f_test), body=f_orelse, orelse=[]
        )
        
        f_body.insert(0, guard)  # NOTE: requires fix_missing_locations
        
        result = ast.FunctionDef(
            name=f_name,
            args=f_args,
            body=f_body,
            decorator_list=f_decorator_list,
        )
        return InPlace(result)


class DoubleNegation(Rule):
    
    def match(self, node: AST) -> bool:
        match node:
            case(
                ast.UnaryOp(
                    op=ast.Not(),
                    operand=ast.UnaryOp(op=ast.Not(), operand=_))
                ):
                return True
            case _:
                return False
    
    def change(self, node: AST) -> InPlace | None:
        if not self.match(node): return None
        
        result = node.operand.operand
        
        return InPlace(result)


class DeMorgan(Rule):
    
    def match(self, node: AST) -> bool:
        match node:
            case( 
                ast.UnaryOp(
                    op=ast.Not(),
                    operand=ast.BoolOp(op=ast.And() | ast.Or(), values=_))
                ):
                return True
            case _:
                return False
    
    def change(self, node: AST) -> InPlace | None:
        if not self.match(node): return None
        
        values = [ 
            ast.UnaryOp(op=ast.Not(), operand=value)
            for value in node.operand.values
        ]
        
        if isinstance(node.operand.op, ast.And):
            result = ast.BoolOp(
                op=ast.Or(),
                values=values
            )
            return InPlace(result)
        
        if isinstance(node.operand.op, ast.Or):
            result = ast.BoolOp(
                op=ast.And(),
                values=values
            )
            return InPlace(result)
