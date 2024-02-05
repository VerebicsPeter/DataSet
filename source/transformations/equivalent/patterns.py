from typing import Callable
import ast
from ast import AST, Load, Store, stmt, expr
from ast import *

from ..utils.helpers import Node


def for_pattern(node: For, name: str,
    statement: Callable[[AST, str], AST | None]) -> For | None:
    match node:
        case(
            For(
                target=Name(ctx=Store()),
                body=[
                    If(test=_, body=[_pattern], orelse=[])
                    |
                    _pattern
                ],
                orelse=[]) as _for
            ):
            if len(Node.all_names(_for, name)) - 1:
                return None
            if statement(_pattern, name):
                return node


class Patterns:
    
    @staticmethod
    def assign_empty_list(node: AST) -> Assign | None:
        match node:
            case(
                Assign(targets=[Name(ctx=Store())], value=List(elts=[], ctx=Load()))
                ):
                return node

    @staticmethod
    def assign_empty_dict(node: AST) -> Assign | None:
        match node:
            case( 
                Assign(targets=[Name(ctx=Store())], value=Dict(keys=[], values=[]))
                ):
                return node

    @staticmethod
    def assign_empty_set(node: AST) -> Assign | None:
        match node:
            case(
                Assign(targets=[Name(ctx=Store())], value=Call(func=Name('set', ctx=Load()), args=[], keywords=[]))
                ):
                return node
    
    @staticmethod
    def assign_zero_numeric(node: AST) -> Assign | None:
        match node:
            case(
                Assign(targets=[Name(ctx=Store())], value=(Constant(0) | Constant(0.0)))
                ):
                return node
    
    @staticmethod
    def adds_to_list(node: AST, name: str) -> AST | None:
        match node:
            case(
                Expr(
                    value=Call(
                        func=Attribute(
                                value=Name(id=_ as _name),
                                attr='append',
                                ctx=Load()),
                        args=_))
                ):
                if name == _name: return node

    @staticmethod
    def adds_to_dict(node: AST, name: str) -> AST | None:
        match node:
            case(
                Assign(
                    targets=[
                        Subscript(
                            value=Name(id=_ as _name),
                            slice=_,
                            ctx=Store())],
                    value=_)
                ):
                if name == _name: return node

    @staticmethod
    def adds_to_set(node: AST, name: str) -> AST | None:
        match node:
            case(
                Expr(
                    value=Call(
                        func=Attribute(
                                value=Name(id=_ as _name),
                                attr='add',
                                ctx=Load()),
                        args=_))
                ):
                if name == _name: return node

    @staticmethod
    def adds_to_numeric(node: AST, name: str) -> AST | None:
        match node:
            case(
                AugAssign(
                        target=Name(id=_ as _name),
                        op=Add(),
                        value=_)
                ):
                if name == _name: return node

    @staticmethod
    def for_to_list_comp(node: For, name: str) -> For | None:
        return for_pattern(node, name, Patterns.adds_to_list)
    
    @staticmethod
    def for_to_dict_comp(node: For, name: str) -> For | None:
        return for_pattern(node, name, Patterns.adds_to_dict)
    
    @staticmethod
    def for_to_set_comp(node: For, name: str) -> For | None:
        return for_pattern(node, name, Patterns.adds_to_set)

    @staticmethod
    def for_to_sum(node: For, name: str) -> For | None:
        return for_pattern(node, name, Patterns.adds_to_numeric)
