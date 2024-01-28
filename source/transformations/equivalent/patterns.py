import ast
from ast import AST, Load, Store, stmt, expr
from ast import *

from ..utils.helpers import Node

class Patterns:

    @staticmethod
    def assign_empty_list(node: AST) -> Assign | None:
        match node:
            case(
                Assign(targets=[Name(ctx=Store())], value=List(elts=[], ctx=Load()))
            ):
                return node

    @staticmethod
    def for_to_list_comp(node: AST, name: str) -> For | None:
        match node:
            case(
                For(
                    target=Name(),
                    body=[
                        Expr(
                            value=Call(
                                func=Attribute(
                                        value=Name(id=_ as _name),
                                        attr='append',
                                        ctx=Load()),
                                args=_))
                    |
                        If(
                            test=_,
                            body=[
                                Expr(
                                    value=Call(
                                        func=Attribute(
                                                value=Name(id=_ as _name),
                                                attr='append',
                                                ctx=Load()),
                                        args=_))
                            ],
                            orelse=[])
                    ],
                    orelse=[]
                ) as _for
            ):
                if len(Node.all_names(_for, name)) - 1:
                    return None
                if name == _name:
                    return node

