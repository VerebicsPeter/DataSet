    # TODO: this should handle parsing the ast not the application

import ast

from ast import parse, unparse, dump, iter_child_nodes, AST

import copy

from typing import Protocol

from transformations.transformation import (
    AST, NodeVisitor
)

from transformations.equivalent.visitors import (
    TFor, TIf, TFunctionDef, TLogic
)

from transformations.equivalent.rules import (
    # for rules
    ForToListComprehension,
    ForToDictComprehension,
    ForToSetComprehension,
    ForToSum,
    # if rules
    InvertIf,
    # function def rules
    ExtractFunctionDefGuard,
    # logic rules
    DoubleNegation,
    DeMorgan
)

class CustomVisitor(Protocol):
    changed: True
    
    def transform_ast(node: AST):
        ...

class TransformationBuilder:
    
    def __init__(self, initial_ast: AST = None) -> None:
        self._ast    = initial_ast
        self.changed = False
        self.queue: list[CustomVisitor] = []
    
    def set_ast(self, initial_ast: AST) -> None:
        self._ast = initial_ast
    
    def get_ast(self) -> AST | None: return self._ast
    
    def add_one(self, visitor: NodeVisitor):
        self.queue.append(visitor)
        return self
    
    def add(self, *visitors: NodeVisitor):
        self.queue.extend(visitors)
        return self
    
    def run(self):
        if not self._ast:
            print("AST needed for running the transformation!")
            return
        
        while self.queue:
            visitor = self.queue.pop(0)
            visitor.transform_ast(self._ast)
            self.changed = self.changed or visitor.changed
        return self


class CopyTransformer():

    def __init__(self, ast: AST):
        self.ast = copy.deepcopy(ast)
        self.changed = False
        
    def change(self) -> str:
        if not self.changed:
            return ""
        return unparse(self.ast)

    def apply_for_to_comprehension(self):
        diff= for_to_comprehension(self.ast)
        self.changed = self.changed or diff
        return self

    def apply_invert_if(self):
        diff= invert_if(self.ast)
        self.changed = self.changed or diff
        return self
    
    def apply_def_guard(self):
        diff= def_guard(self.ast)
        self.changed = self.changed or diff
        return self
    
    def apply_logic_rules(self):
        diff= logic_rules(self.ast)
        self.changed = self.changed or diff
        return self
    
    def apply_all(self):
        diff= all_transformations(self.ast)
        self.changed = self.changed or diff
        return self


def safe_parse(source: str):
    try:
        return ast.parse(source)
    except Exception as exception: print(exception)


# Transformation "presets"


def for_to_comprehension(node: AST):
    t = TransformationBuilder(node)\
        .add(TFor(ForToListComprehension()))\
        .add(TFor(ForToDictComprehension()))\
        .add(TFor(ForToSetComprehension()))\
        .add(TFor(ForToSum()))\
        .run()
    return t.changed


def invert_if(node: AST):
    t = TransformationBuilder(node)\
        .add(TIf(InvertIf()))\
        .run()
    return t.changed


def def_guard(node: AST):
    t = TransformationBuilder(node)\
        .add(TFunctionDef(ExtractFunctionDefGuard()))\
        .run()
    return t.changed

    
def logic_rules(node: AST):
    t = TransformationBuilder(node)\
        .add(TLogic(DoubleNegation()))\
        .add(TLogic(DeMorgan()))\
        .run()
    return t.changed


def all_transformations(node: AST):
    return any([for_to_comprehension(node),def_guard(node),invert_if(node),logic_rules(node)])
